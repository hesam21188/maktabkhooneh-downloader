import typer

from rich.console import Console


from .menus import download_menu, login_menu
from .auth.login import check_login

console = Console()
app = typer.Typer()


def handle_login():
    sessionid = check_login().strip()
    if not sessionid:
        login_menu()
        handle_login()
    else:
        if download_menu(sessionid) == 2:
            handle_login()


@app.command()
def start():
    console.print("[bold cyan]maktabkhooneh downloader[/bold cyan]")
    handle_login()


if __name__ == "__main__":
    app()
