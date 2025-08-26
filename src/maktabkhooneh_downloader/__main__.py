import typer

from rich.console import Console

from InquirerPy import inquirer
from InquirerPy.base.control import Choice


from .auth.login import check_login, login_menu
from .download.downloader import get_course

console = Console()
app = typer.Typer()


@app.command()
def start():
    console.print("[bold cyan]maktabkhooneh downloader[/bold cyan]")
    sessionid = check_login()
    if not sessionid:
        login_menu()
    else:
        choice = inquirer.select(
            message=f"logged in as sessionid: {sessionid}",
            choices=[
                Choice(
                    value=get_course,
                    name="start download 🚀",
                ),
                Choice(value=login_menu, name="change (login again) 🔄"),
                Choice(value=exit, name="🚪 Exit"),
            ],
        ).execute()
    choice()


if __name__ == "__main__":
    app()
