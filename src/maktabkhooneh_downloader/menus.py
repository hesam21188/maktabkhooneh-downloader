import re
from InquirerPy import inquirer
from InquirerPy.separator import Separator
from InquirerPy.base.control import Choice
from click.utils import R
from .download.downloader import start_download
from .auth.login import auto_login, manual_login
from maktabkhooneh_downloader.auth import login


def download_menu(sessionid):
    choice = inquirer.select(
        message=f"logged in as sessionid: {sessionid}",
        choices=[
            Choice(
                value=lambda: start_download(sessionid),
                name="start download 🚀",
            ),
            Choice(
                value=login_menu,
                name="change (login again) 🔄",
            ),
            Choice(value=exit, name="🚪 Exit"),
        ],
    ).execute()
    return choice()


def login_menu():
    choice = inquirer.select(
        message="Select an option for login:",
        choices=[
            Choice(
                value=auto_login,
                name="🔥 Auto login (from your browser cookies)",
            ),
            Choice(
                value=manual_login,
                name="⚡ Manual login (enter your session id manually)",
            ),
            Separator(),
            Choice(value=exit, name="🚪 Exit"),
        ],
    ).execute()
    return choice()
