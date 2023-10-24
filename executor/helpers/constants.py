from enum import Enum

DEFAULT_JOB_LIFETIME_MIN = 55

ENV_AWS_ACCESS_KEY_ID = 'AWS_ACCESS_KEY_ID'
ENV_AWS_SECRET_ACCESS_KEY = 'AWS_SECRET_ACCESS_KEY'
ENV_AWS_SESSION_TOKEN = 'AWS_SESSION_TOKEN'
ENV_AWS_DEFAULT_REGION = 'AWS_DEFAULT_REGION'

ENV_AZURE_CLIENT_SECRET = 'AZURE_CLIENT_SECRET'

ENV_DEFAULT_BUCKET_NAME = 'DEFAULT_REPORTS_BUCKET_NAME'
ENV_JOB_ID = 'AWS_BATCH_JOB_ID'
ENV_BATCH_RESULTS_ID = 'BATCH_RESULTS_ID'
ENV_BATCH_RESULTS_IDS = 'BATCH_RESULTS_IDS'

ENV_TARGET_REGIONS = 'TARGET_REGIONS'
ENV_TARGET_RULESETS = 'TARGET_RULESETS'
ENV_TARGET_RULESETS_VIEW = 'TARGET_RULESETS_VIEW'
ENV_LICENSED_RULESETS = 'LICENSED_RULESETS'
ENV_VAR_REGION = 'AWS_REGION'
ENV_VAR_CREDENTIALS = 'CREDENTIALS_KEY'
ENV_VAR_JOB_LIFETIME_MIN = 'JOB_LIFETIME_MIN'
ENV_EVENT_DRIVEN = 'EVENT_DRIVEN'
ENV_SUBMITTED_AT = 'SUBMITTED_AT'
ENV_AFFECTED_LICENSES = 'AFFECTED_LICENSES'
ENV_EXECUTOR_MODE = 'EXECUTOR_MODE'
ENV_SCHEDULED_JOB_NAME = 'SCHEDULED_JOB_NAME'
ENV_JOB_TYPE = 'JOB_TYPE'
ENV_SYSTEM_CUSTOMER_NAME = 'SYSTEM_CUSTOMER_NAME'
ENV_TENANT_NAME = 'TENANT_NAME'
ENV_PLATFORM_ID = 'PLATFORM_ID'
ENV_VAR_STATS_S3_BUCKET_NAME = 'STATS_S3_BUCKET_NAME'
ENV_VAR_RULESETS_BUCKET_NAME = 'RULESETS_BUCKET_NAME'
ENV_ALLOW_MANAGEMENT_CREDS = 'ALLOW_MANAGEMENT_CREDENTIALS'

STANDARD_JOB_TYPE = 'standard'
SCHEDULED_JOB_TYPE_FOR_ENV = 'scheduled'  # ask me
MULTI_ACCOUNT_EVENT_DRIVEN_JOB_TYPE = 'event-driven-multi-account'

CONSISTENT_EXECUTOR_MODE = 'consistent'
CONCURRENT_EXECUTOR_MODE = 'concurrent'

AWS = 'AWS'
AZURE = 'AZURE'
GOOGLE = 'GOOGLE'
GCP = 'GCP'
KUBERNETES = 'KUBERNETES'

ENV_GOOGLE_APPLICATION_CREDENTIALS = 'GOOGLE_APPLICATION_CREDENTIALS'
ENV_CLOUDSDK_CORE_PROJECT = 'CLOUDSDK_CORE_PROJECT'

READY_TO_SCAN_CODE = 'READY_TO_SCAN'

STEP_GET_BATCH_RESULTS_ED = 'get BatchResults for event-driven job'
STEP_BATCH_RESULT_ALREADY_SUCCEEDED = 'batch result has already succeeded'
STEP_GET_TENANT = 'get tenant'
STEP_GRANT_JOB = 'grant job execution'
STEP_DOWNLOAD_RULES = 'download rules content'
STEP_GET_CREDENTIALS_CONFIGURATION = 'get credentials configuration'
STEP_ASSERT_CREDENTIALS = 'assert temporary cloud credentials'
STEP_ASSUME_ROLE = 'assume role'
STEP_EXPORT_CREDENTIALS = 'export temporary cloud credentials'
STEP_LOAD_POLICIES = 'load policies'
STEP_COLLECT_STATISTICS = 'collect statistics'

INVALID_CREDENTIALS_ERROR_CODES = {
    AWS: {'AuthFailure', 'InvalidToken',
          'UnrecognizedClientException', 'ExpiredToken',
          'ExpiredTokenException'},  # add 'InvalidClientTokenId'
    AZURE: {'InvalidAuthenticationTokenTenant',
            'AuthorizationFailed', 'ClientAuthenticationError',
            'Azure Error: AuthorizationFailed'},
    GOOGLE: set()
}
ACCESS_DENIED_ERROR_CODE = {
    AWS: {
        'AccessDenied', 'AccessDeniedException', 'UnauthorizedOperation',
        'AuthorizationError', 'AccessDeniedException, AccessDeniedException'
    },  # epam-aws-399-appflow_encrypted_with_kms_cm
    AZURE: set(),
    GOOGLE: set()
}
AWS_DEFAULT_REGION = 'us-east-1'
AZURE_COMMON_REGION = 'AzureCloud'
GCP_COMMON_REGION = 'us-central1'
MULTIREGION = 'multiregion'
FINDINGS_FOLDER = 'findings'

CUSTOMER_ATTR = 'customer'
TENANT_ATTR = 'tenant'
RULESETS_ATTR = 'rulesets'
RULESET_CONTENT_ATTR = 'ruleset_content'

CUSTODIAN_TYPE = 'CUSTODIAN'
CUSTODIAN_LICENSES_TYPE = 'CUSTODIAN_LICENSES'  # contains licenses
SCHEDULED_JOB_TYPE = 'SCHEDULED_JOB'
TENANT_ENTITY_TYPE = 'TENANT'

RULES_TO_EXCLUDE = 'rules_to_exclude'

KID_ATTR = 'kid'
ALG_ATTR = 'alg'
TYP_ATTR = 'typ'
CLIENT_TOKEN_ATTR = 'client-token'

PRODUCT_TYPE_NAME_ATTR = 'product_type_name'
PRODUCT_NAME_ATTR = 'product_name'
ENGAGEMENT_NAME_ATTR = 'engagement_name'
TEST_TITLE_ATTR = 'test_title'

POST_METHOD = 'POST'
PATCH_METHOD = 'PATCH'

ITEMS_PARAM = 'items'
MESSAGE_PARAM = 'message'
AUTHORIZATION_PARAM = 'authorization'

# on-prem
ENV_SERVICE_MODE = 'SERVICE_MODE'
DOCKER_SERVICE_MODE, SAAS_SERVICE_MODE = 'docker', 'saas'

ENV_MONGODB_USER = 'MONGO_USER'
ENV_MONGODB_PASSWORD = 'MONGO_PASSWORD'
ENV_MONGODB_URL = 'MONGO_URL'  # host:port
ENV_MONGODB_DATABASE = 'MONGO_DATABASE'  # custodian_as_a_service

ENV_MINIO_HOST = 'MINIO_HOST'
ENV_MINIO_PORT = 'MINIO_PORT'
ENV_MINIO_ACCESS_KEY = 'MINIO_ACCESS_KEY'
ENV_MINIO_SECRET_ACCESS_KEY = 'MINIO_SECRET_ACCESS_KEY'

ENV_VAULT_TOKEN = 'VAULT_TOKEN'
ENV_VAULT_HOST = 'VAULT_URL'
ENV_VAULT_PORT = 'VAULT_SERVICE_SERVICE_PORT'  # env from Kubernetes

ENVS_TO_HIDE = {
    'PS1', 'PS2', 'PS3', 'PS4', ENV_MONGODB_USER, ENV_MONGODB_PASSWORD,
    ENV_MINIO_ACCESS_KEY, ENV_MINIO_SECRET_ACCESS_KEY, ENV_VAULT_TOKEN,
    ENV_AWS_SECRET_ACCESS_KEY, ENV_AWS_SESSION_TOKEN, ENV_AZURE_CLIENT_SECRET
}
HIDDEN_ENV_PLACEHOLDER = '****'


class JobState(str, Enum):
    """
    https://docs.aws.amazon.com/batch/latest/userguide/job_states.html
    """
    SUBMITTED = 'SUBMITTED'
    PENDING = 'PENDING'
    RUNNABLE = 'RUNNABLE'
    STARTING = 'STARTING'
    RUNNING = 'RUNNING'
    FAILED = 'FAILED'
    SUCCEEDED = 'SUCCEEDED'


# custodian parent
ALL = 'ALL'
SCOPE_ATTR = 'scope'
CLOUDS_ATTR = 'clouds'

COMPOUND_KEYS_SEPARATOR = '#'

ED_AWS_RULESET_NAME = '_ED_AWS'
ED_AZURE_RULESET_NAME = '_ED_AZURE'
ED_GOOGLE_RULESET_NAME = '_ED_GOOGLE'

KEY_RULES_TO_SEVERITY = 'RULES_TO_SEVERITY'
KEY_RULES_TO_STANDARDS = 'RULES_TO_STANDARDS'
KEY_HUMAN_DATA = 'HUMAN_DATA'
