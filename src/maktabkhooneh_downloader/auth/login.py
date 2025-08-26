from typing import Dict, Any

from InquirerPy import inquirer
from InquirerPy.base.control import Choice


from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text
from pathlib import Path
import json

CREDS_PATH: Path = Path.home() / ".maktabkhooneh_dl" / "session.json"
CREDS_PATH.parent.mkdir(parents=True, exist_ok=True)

console = Console()


def _load_json() -> Dict[str, Any]:
    """Load existing credentials, return empty dict if file doesn't exist."""
    if not CREDS_PATH.exists():
        return {}
    try:
        with CREDS_PATH.open("r", encoding="utf-8") as fp:
            return json.load(fp)
    except (json.JSONDecodeError, OSError):
        return {}


def _save_json(data: Dict[str, Any]) -> None:
    """Save dictionary to JSON file."""
    with CREDS_PATH.open("w", encoding="utf-8") as fp:
        json.dump(data, fp, indent=2, ensure_ascii=False)


def auto_login():
    pass


def manual_login():
    console.print(
        Panel(
            Text(
                "Enter the session id copied from your browser cookies "
                "(usually named `sessionid` or `session`).",
                style="cyan",
            ),
            title="Manual Login",
            border_style="bright_blue",
        )
    )

    session_id = Prompt.ask("Session id", console=console).strip()
    if not session_id:
        console.print("[red]Session id cannot be empty.[/red]")
        manual_login()
        return

    creds = _load_json()
    creds["session_id"] = session_id
    _save_json(creds)

    console.print(
        Panel(
            Text("Session id saved successfully!", style="bold green"),
            border_style="green",
        )
    )


def check_login() -> str:
    """
    Returns the stored session_id if it exists, otherwise an empty string.
    """
    return _load_json().get("session_id", "")


def login_menu():
    choice = inquirer.select(
        message="Select an option for login:",
        choices=[
            Choice(value=auto_login, name="🔥 Auto login (from your browser cookies)"),
            Choice(
                value=manual_login,
                name="⚡ Manual login (enter your session id manually)",
            ),
            Choice(value=exit, name="🚪 Exit"),
        ],
    ).execute()
    choice()
