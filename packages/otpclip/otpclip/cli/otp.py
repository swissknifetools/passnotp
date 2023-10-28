from pathlib import Path

import click
from otpclip.command.create import create_otp
from otpclip.command.delete import delete_otp
from otpclip.query.get import get_otp
from otpclip.query.list import list_otp
from shared.toml import get_version_from_toml


@click.group(name="otpclip", invoke_without_command=True)
@click.pass_context
@click.version_option(version=get_version_from_toml(Path("../../pyproject.toml")), prog_name='otpclip', message='%(version)s')
def cli_otp(ctx: click.Context) -> None:
    """
    
    A streamlined command-line utility designed for seamless one-time-password (OTP) management. With otpclip, you can effortlessly handle OTPs directly from your terminal, enhancing your authentication workflow without the need for additional applications or interfaces.
    
    Author: Joni Seraj, Ergi Kame
    
    """
    if ctx.invoked_subcommand is None and not ctx.args:
        click.echo(ctx.get_help())
    elif ctx.invoked_subcommand is None:
        ctx.invoke(get)
    
@click.command()
def list() -> None:
    """Print a list of OTPs."""
    list_otp()
    
@click.command()
def get() -> None:
    """Copies OTP code to your clipboard."""
    get_otp()
    
@click.command()
@click.argument('identifier')
@click.argument('key')
def create(identifier: str, key: str) -> None:
    """Create OTP."""
    create_otp(identifier, key)
    
@click.command()
def delete() -> None:
    """Delete OTP."""
    delete_otp()
    
cli_otp.add_command(list)
cli_otp.add_command(get)
cli_otp.add_command(create)
cli_otp.add_command(delete)
