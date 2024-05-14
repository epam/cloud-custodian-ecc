import click

from c7ncli.group import (
    ContextObj,
    ViewCommand,
    build_tenant_option,
    cli_response,
    response,
)
from c7ncli.service.constants import AWS, AZURE, GOOGLE, KUBERNETES


@click.group(name='sre')
def sre():
    """
    Manages Rule engine integration (self integration for Maestro)
    :return:
    """


@sre.command(cls=ViewCommand, name='add')
@build_tenant_option(multiple=True)
@click.option('--all_tenants', is_flag=True,
              help='Whether to activate integration for all tenants')
@click.option('--clouds', '-cl',
              type=click.Choice((AWS, AZURE, GOOGLE, KUBERNETES)),
              multiple=True,
              help='Tenant clouds to activate this dojo for. '
                   'Can be specific together with --all_tenants flag')
@click.option('--exclude_tenant', '-et', type=str, multiple=True,
              help='Tenants to exclude for this integration. '
                   'Can be specified together with --all_tenants flag')
@click.option('--description', '-d', type=str, required=True,
              help='Human-readable description of this installation')
@click.option('--username', '-u', type=str, required=True,
              help='Username to set to the application')
@click.option('--password', '-p', type=str, required=True,
              help='Password to set to application')
@click.option('--url', '-U', type=str,
              help='Url to Custodian installation')
@click.option('--auto_resolve_access', '-ara', is_flag=True,
              help='If specified, Custodian will try to '
                   'resolve access automatically. '
                   'Otherwise you must specify url')
@click.option('--results_storage', '-rs', type=str,
              help='S3 bucket name were to store EC2 recommendations')
@cli_response()
def add(ctx: ContextObj, tenant_name: tuple[str, ...], all_tenants: bool,
        clouds: tuple[str], exclude_tenant: tuple[str, ...],
        description: str, username: str, password: str, url: str | None,
        auto_resolve_access: bool,
        results_storage: str | None, customer_id: str | None):
    """
    Adds self integration
    """
    if tenant_name and any((all_tenants, clouds, exclude_tenant)):
        return response('Do not provide --all_tenants, --clouds or '
                        '--exclude_tenants if --tenant_name given')
    if not all_tenants and not tenant_name:
        return response('Either --all_tenants or --tenant_name must be given')
    if (clouds or exclude_tenant) and not all_tenants:
        return response('set --all_tenants if you provide --clouds or '
                        '--exclude_tenants')
    if auto_resolve_access and url:
        return response('Do not provide --url if --auto_resolve_access is set')
    return ctx['api_client'].sre_add(
        description=description,
        username=username,
        password=password,
        auto_resolve_access=auto_resolve_access,
        url=url,
        results_storage=results_storage,
        tenant_names=tenant_name,
        all_tenants=all_tenants,
        clouds=clouds,
        exclude_tenant=exclude_tenant,
        customer_id=customer_id
    )


@sre.command(cls=ViewCommand, name='describe')
@cli_response()
def describe(ctx: ContextObj, customer_id):
    """
    Describes self integration
    """
    return ctx['api_client'].sre_describe(customer_id=customer_id)


@sre.command(cls=ViewCommand, name='delete')
@cli_response()
def delete(ctx: ContextObj, customer_id):
    """
    Deletes self integration
    """
    return ctx['api_client'].sre_delete(customer_id=customer_id)


@sre.command(cls=ViewCommand, name='update')
@click.option('--add_tenant', '-at', type=str, multiple=True,
              help='Tenants to activate')
@click.option('--exclude_tenant', '-et', type=str, multiple=True,
              help='Tenants to deactivate')
@cli_response()
def update(ctx: ContextObj, customer_id, add_tenant, exclude_tenant):
    """
    Allows to add and remove specific tenants from the activation
    """
    return ctx['api_client'].sre_update(
        add_tenants=add_tenant,
        remove_tenants=exclude_tenant,
        customer_id=customer_id
    )
