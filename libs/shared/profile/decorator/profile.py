import click

def profile_decorator(func):
    @click.option('--profile', default='default', help='Select configuration profile')
    @click.pass_context
    def wrapper(ctx, *args, **kwargs):
        ctx.ensure_object(dict)
        ctx.obj['profile'] = kwargs.pop('profile')
        return ctx.invoke(func, *args, **kwargs)
    return wrapper