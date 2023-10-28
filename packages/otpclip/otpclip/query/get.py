import subprocess
from otpclip.config.logging import logger

def get_otp() -> None:
    result = subprocess.run(['cloak', 'view'], capture_output=True, text=True)
    
    if(result.returncode == 0) :
        print(result.stdout)
    else:
        print(result.stderr)