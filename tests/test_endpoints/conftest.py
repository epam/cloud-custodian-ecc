import json
import uuid
from datetime import timedelta, datetime
from typing import TYPE_CHECKING

import boto3
import pytest
from dateutil.relativedelta import relativedelta, SU
from moto.backends import get_backend
from webtest import TestApp

from helpers.constants import Permission, CAASEnv, PolicyEffect, JobState
from helpers.time_helper import utc_iso, utc_datetime
from services import SP  # probably the only safe import we can use in conftest
from ..commons import SOURCE, InMemoryHvacClient, SREClient

if TYPE_CHECKING:
    from modular_sdk.models.tenant import Tenant
    from modular_sdk.models.customer import Customer


# assuming that only this package will use mongo so that we need to clear
# it after each invocation

# data sources fixtures
@pytest.fixture(autouse=True)
def mocked_mongo_client(request):
    client = request.config.mongo_client
    yield client
    for db in client.list_database_names():
        client.drop_database(db)


@pytest.fixture(autouse=True)
def mocked_s3_client(request):
    yield boto3.client('s3')
    get_backend('s3').reset()


@pytest.fixture(autouse=True)
def mocked_hvac_client(request):
    yield InMemoryHvacClient()
    InMemoryHvacClient.reset()


# logic fixtures

@pytest.fixture(autouse=True)
def vault_token(mocked_hvac_client) -> None:
    # just test key
    mocked_hvac_client.secrets.kv.v2.create_or_update_secret(
        path='rule-engine-private-key',
        secret={
            'data': 'LS0tLS1CRUdJTiBQUklWQVRFIEtFWS0tLS0tCk1JSHVBZ0VBTUJBR0J5cUdTTTQ5QWdFR0JTdUJCQUFqQklIV01JSFRBZ0VCQkVJQXRGcnczSW43QzZuK01hSHEKK3BJQnBiejVjUzI5V202RVRidUpCbmJUeUhYZ0V2cjBNcXFLT25qemY1VCtoSGZodVhYSSs5VE5VR1dCekl0Rgo4THRhVGltaGdZa0RnWVlBQkFBbUs4U25HYUkyVHNJRXAzMDZIRWgzZXNTNHNLUXZ4QXNmY0R4ZUVEVW1GUGxhCkhKejUyM2MzMVJXRGNLaXR1cXFpUXlOYjZvdEM3MXZMdjNXNCswSW9Bd0NGc0RUWVVqMHl1SmU4TjBWblNYSHMKOWpFOWR2L2dPSUYreG1YMjI1bnIzZnU4UHhiWDZXdlFhQjcwUTZ2WUlsOGtCNStSaTA2WkxESms2cHBCdHM0SApHUT09Ci0tLS0tRU5EIFBSSVZBVEUgS0VZLS0tLS0K'},  # noqa
        mount_point='kv'
    )


@pytest.fixture(autouse=True)
def s3_buckets(mocked_s3_client) -> None:
    buckets = [
        CAASEnv.REPORTS_BUCKET_NAME.get(),
        CAASEnv.STATISTICS_BUCKET_NAME.get(),
        CAASEnv.RULESETS_BUCKET_NAME.get(),
        CAASEnv.METRICS_BUCKET_NAME.get(),
        CAASEnv.RECOMMENDATIONS_BUCKET_NAME.get()
    ]
    for b in buckets:
        SP.s3.create_bucket(b, 'eu-central-1')


@pytest.fixture()
def system_user(mocked_mongo_client, vault_token) -> tuple[str, str]:
    """
    Creates system policy, role and user
    """
    from models.user import User
    SP.policy_service.create(
        customer=CAASEnv.SYSTEM_CUSTOMER_NAME.get(),
        name='system',
        description='system policy',
        permissions=[p.value for p in Permission],
        tenants=['*'],
        effect=PolicyEffect.ALLOW
    ).save()
    SP.role_service.create(
        customer=CAASEnv.SYSTEM_CUSTOMER_NAME.get(),
        name='system',
        expiration=None,
        policies=['system'],
        description='system role',
    )
    col = mocked_mongo_client[CAASEnv.MONGO_DATABASE.get()][User.Meta.table_name]
    col.insert_one({
        'user_id': 'system',
        'customer': CAASEnv.SYSTEM_CUSTOMER_NAME.get(),
        'role': 'system',
        'created_at': utc_iso(),
        'password': b'$2b$12$KZdrVss.Juxf.HB/TjtqvefpSNTW7gUdXLxLTXJXv7.3bCiDNqpXm'  # noqa
    })
    # here i just hardcode the hashed password directly in order to bypass
    #  bcrypt. It's intentionally slow for security purposes and it makes all
    #  tests run much slower.
    # SP.users_client.signup_user(
    #     username='system',
    #     password='system',
    #     customer=CAASEnv.SYSTEM_CUSTOMER_NAME.get(),
    #     role='system'
    # )
    return 'system', 'system'


@pytest.fixture()
def system_user_token(system_user) -> str:
    return SP.users_client.authenticate_user(
        username=system_user[0],
        password=system_user[1]
    )['id_token']


@pytest.fixture(scope='session')
def deployment_resources():
    name = 'deployment_resources.json'
    with open(SOURCE / name, 'r') as f:
        data1 = json.load(f).get('custodian-as-a-service-api') or {}
    with open(SOURCE / 'validators' / name, 'r') as f:
        data2 = json.load(f).get('custodian-as-a-service-api') or {}
    data1['models'] = data2.get('models') or {}
    return data1


@pytest.fixture(
    scope='session')  # todo think about scope and look at the performance
def wsgi_app(deployment_resources):
    from onprem.api.app import OnPremApiBuilder
    from onprem.api.deployment_resources_parser import \
        DeploymentResourcesApiGatewayWrapper
    dr_wrapper = DeploymentResourcesApiGatewayWrapper(deployment_resources)
    builder = OnPremApiBuilder(dr_wrapper)
    return builder.build()


@pytest.fixture(scope='session')
def wsgi_test_app(wsgi_app) -> TestApp:
    return TestApp(wsgi_app)


@pytest.fixture(scope='session')
def sre_client(wsgi_test_app) -> SREClient:
    return SREClient(wsgi_test_app)


# override existing fixtures only for this package because here we have all
# the inner services mocked
@pytest.fixture()
def main_customer(mocked_mongo_client, main_customer: 'Customer'
                  ) -> 'Customer':
    main_customer.save()
    return main_customer


@pytest.fixture()
def aws_tenant(main_customer: 'Customer', aws_tenant: 'Tenant') -> 'Tenant':
    aws_tenant.save()
    return aws_tenant


@pytest.fixture()
def azure_tenant(main_customer: 'Customer', azure_tenant: 'Tenant'
                 ) -> 'Tenant':
    azure_tenant.save()
    return azure_tenant


@pytest.fixture()
def google_tenant(main_customer: 'Customer', google_tenant: 'Tenant'
                  ) -> 'Tenant':
    google_tenant.save()
    return google_tenant


@pytest.fixture()
def create_tenant_job():
    def factory(tenant, submitted_at,
                status: JobState = JobState.SUCCEEDED):
        from models.job import Job
        return Job(
            id=str(uuid.uuid4()),
            batch_job_id='batch_job_id',
            tenant_name=tenant.name,
            customer_name=tenant.customer_name,
            status=status.value,
            submitted_at=utc_iso(submitted_at),
            created_at=utc_iso(submitted_at + timedelta(minutes=1)),
            started_at=utc_iso(submitted_at + timedelta(minutes=2)),
            stopped_at=utc_iso(submitted_at + timedelta(minutes=5)),
            rulesets=['TESTING']
        )

    return factory


@pytest.fixture()
def create_tenant_br():
    def factory(tenant, submitted_at,
                status: JobState = JobState.SUCCEEDED):
        from models.batch_results import BatchResults
        return BatchResults(
            id=str(uuid.uuid4()),
            job_id='batch_job_id',
            status=status.value,
            cloud_identifier=tenant.project,
            tenant_name=tenant.name,
            customer_name=tenant.customer_name,
            submitted_at=utc_iso(submitted_at),
            stopped_at=utc_iso(submitted_at + timedelta(minutes=5)),
        )

    return factory


@pytest.fixture()
def report_bounds() -> tuple[datetime, datetime]:
    """
    Returns tuple that contains two dates. Last Sunday and next Sunday
    """
    now = utc_datetime()
    start = now + relativedelta(hour=0, minute=0, second=0, microsecond=0,
                                weekday=SU(-1))
    end = now + relativedelta(hour=0, minute=0, second=0, microsecond=0,
                              weekday=SU(+1))
    return start, end


@pytest.fixture()
def reports_marker(report_bounds) -> None:
    """
    Set mocked dates marker
    """
    from models.setting import Setting
    from services.setting_service import SettingKey
    start, end = report_bounds
    start = start.date()
    end = end.date()
    Setting(
        name=SettingKey.REPORT_DATE_MARKER,
        value={
            "current_week_date": end.isoformat(),
            "last_week_date": start.isoformat()
        }
    ).save()
