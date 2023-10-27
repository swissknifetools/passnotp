import click
from otpclip.command.create import create_otp
from otpclip.command.delete import delete_otp
from otpclip.query.get import get_otp
from otpclip.query.list import list_otp

@click.group(name="otpclip", invoke_without_command=True)
@click.pass_context
def cli_otp(ctx: click.Context):
    """OTP-related command description."""
    if ctx.invoked_subcommand is None and not ctx.args:
        click.echo(ctx.get_help())
    elif ctx.invoked_subcommand is None:
        ctx.invoke(get)
    
@click.command()
def list():
    """Print a list of OTPs."""
    list_otp()
    
@click.command()
def get():
    """Copies OTP code to your clipboard."""
    get_otp()
    
@click.command()
def create():
    """Create OTP."""
    create_otp()
    
@click.command()
def delete():
    """Delete OTP."""
    delete_otp()
    
cli_otp.add_command(list)
cli_otp.add_command(get)
cli_otp.add_command(create)
cli_otp.add_command(delete)
