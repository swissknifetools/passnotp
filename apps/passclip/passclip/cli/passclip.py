import typer
from passclip.app.core.logging.logging import logger

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])
cli = typer.Typer(context_settings=CONTEXT_SETTINGS)


@cli.command(no_args_is_help=True)
def add() -> None:
    logger.info("add")


@cli.command(no_args_is_help=True)
def rm() -> None:
    logger.info("rm")


@cli.command(no_args_is_help=True)
def ls() -> None:
    logger.info("ls")


@cli.command()
def get(ctx: typer.Context) -> None:
    # logger.debug(ctx.obj)
    logger.info("get")


@cli.callback()
def getCommand(ctx: typer.Context) -> None:
    logger.debug("callback")
    # logger.debug("GET")
    # if ctx.args.__len__() == 0:
    #     ctx.get_help()
    #     exit(0)
    # ctx.invoke(get)


@cli.callback()
def common(ctx: typer.Context, profile: str = typer.Option(default="default", help="Profile")):
    logger.debug("profile")
    # ctx.ensure_object(dict)
    # ctx.obj = profile
