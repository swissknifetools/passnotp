from email.policy import default
from pathlib import Path

import click
from click_default_group import DefaultGroup
from otpclip.app.otp.command.create import create_otp
from otpclip.app.otp.command.delete import delete_otp
from otpclip.app.otp.query.get import get_otp
from otpclip.app.otp.query.list import list_otp
from otpclip.app.core.logging.logging import logger
from shared.toml import get_version_from_toml


@click.group(name="otpclip", cls=DefaultGroup, default='get')
@click.pass_context
@click.version_option(version=get_version_from_toml(Path("../../pyproject.toml")), prog_name='otpclip', message='%(version)s')
def cli_otp(ctx: click.Context) -> None:
    """
    
    A streamlined command-line utility designed for seamless one-time-password (OTP) management. With otpclip, you can effortlessly handle OTPs directly from your terminal, enhancing your authentication workflow without the need for additional applications or interfaces.
    
    Author: Joni Seraj, Ergi Kame
    
    """
    pass
        
@click.command()
@click.argument('id', type=click.STRING)
@click.argument('key', type=click.STRING)
def create(id: str, key: str) -> None:
    """Create OTP."""
    logger.debug(f"otp|create id={id} key={key}")
    create_otp(id, key)
    
@click.command()
@click.argument('id', type=click.STRING)
def delete(id: str) -> None:
    """Delete OTP."""
    logger.debug(f"otp|delete id={id}")
    delete_otp(id)    


@click.command()
@click.argument('pre', type=click.STRING)
def list(pre: str) -> None:
    """Print a list of OTPs."""
    logger.debug(f"otp|list pre={pre}")
    list_otp(pre)
    
@click.command()
@click.argument('id', type=click.STRING)
def get(id: str) -> None:
    """Copies OTP code to your clipboard."""
    logger.debug(f"otp|get id={id}")
    get_otp(id)

cli_otp.add_command(create)
cli_otp.add_command(delete)
cli_otp.add_command(list)
cli_otp.add_command(get)

