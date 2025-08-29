from codecs import charmap_build
import time
from datetime import datetime, timedelta
from rich.live import Live
from pathlib import Path
from InquirerPy import base, inquirer
import requests
from bs4 import BeautifulSoup
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text
import json
from rich.progress import (
    Progress,
    BarColumn,
    DownloadColumn,
    TextColumn,
    TransferSpeedColumn,
    TimeRemainingColumn,
)
import os

console = Console()
session = requests.Session()


def _check_course(url, sessionid):
    base_url = f"https://maktabkhooneh.org/api/v1/sale/{url}/prices"
    session.cookies.set("sessionid", sessionid)
    r = session.get(base_url)
    if r.status_code == 200:
        if not json.loads(r.text)["can_purchase"]["CONTENT"]:
            return True
    return False


def _get_course_chapters(url):
    base_url = f"https://maktabkhooneh.org/api/v1/courses/{url}/chapters/"
    r = session.get(base_url)
    if r.status_code == 200:
        data = json.loads(r.text)
        chapters = {}
        for chapter in data["chapters"]:
            chapters[f"{chapter["slug"]}-ch{chapter["id"]}"] = [
                unit["slug"]
                for unit in chapter["unit_set"]
                if unit["type"] == "lecture"
            ]

        return chapters


def _get_unit_links(url, chapters):
    base_url = f"https://maktabkhooneh.org/course/{url}"
    unit_links = []
    for chapter in chapters:
        for unit in chapters[chapter]:
            unit_links.append(f"{base_url}/{chapter}/{unit}")
    return unit_links


def _get_video_links(unit_links, high_quality=True):
    for unit in unit_links:
        r = session.get(unit)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "html.parser")
            try:
                if high_quality:
                    yield soup.find_all(
                        "a",
                        attrs={
                            "onclick": lambda x: x and "send_download_event(1)" in x
                        },
                    )[0]["href"]
                else:
                    yield soup.find_all(
                        "a",
                        attrs={
                            "onclick": lambda x: x and "send_download_event(0)" in x
                        },
                    )[0]["href"]
            except IndexError:
                pass


def _download_video(url, filepath):
    """
    Download a video to the specified path with resume support.
    Assumes 'filepath' always includes directory (e.g., 'folder/video.mp4').
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    # Get file size from server
    r = requests.head(url)
    r.raise_for_status()
    total_size = int(r.headers.get("content-length", 0))
    if total_size == 0:
        raise ValueError(
            "Server did not return file size or does not support range requests."
        )

    # Resume logic
    initial_pos = os.path.getsize(filepath) if os.path.exists(filepath) else 0
    if initial_pos >= total_size:
        print(f"✅ {filepath} is already fully downloaded.")
        return

    # Setup progress bar
    progress = Progress(
        "[blue]{task.description}",
        BarColumn(),
        DownloadColumn(),
        TransferSpeedColumn(),
        TimeRemainingColumn(),
    )

    with progress:
        task = progress.add_task(
            f"Downloading {os.path.basename(filepath)}",
            total=total_size,
            completed=initial_pos,
        )
        headers = {"Range": f"bytes={initial_pos}-"} if initial_pos else {}

        with requests.get(url, headers=headers, stream=True) as r:
            r.raise_for_status()
            mode = "ab" if initial_pos > 0 else "wb"
            with open(filepath, mode) as f:
                for chunk in r.iter_content(1024 * 1024):  # 1 MB chunks
                    if chunk:
                        f.write(chunk)
                        progress.advance(task, len(chunk))

    print(f"✅ Download completed: {filepath}")


def _normalize_file_name(unit_links):
    file_name = unit_links[i].split("/")[-2:]
    file_name[0] = "-".join(file_name[0].split("-")[:-1])
    file_name[1:1] = ["/"]
    file_name.append(".mp4")
    file_name = "".join(file_name)
    return str(Path.cwd() / file_name)


def start_download(sessionid, course_url=""):
    if not course_url:
        course_url = Prompt.ask("course url", console=console).strip().split("/")[-1]
    if not _check_course(course_url, sessionid):
        console.print(
            Panel(
                Text("you have to buy the course first", style="bold red"),
                border_style="red",
            )
        )
        return 0
    chapters = _get_course_chapters(course_url)
    unit_links = _get_unit_links(course_url, chapters)

    for i, video_link in enumerate(_get_video_links(unit_links)):
        file_name = _normalize_file_name(unit_links)
        _download_video(video_link, file_name)

    return 1


def video_links_txt(sessionid):
    console = Console()
    course_url = Prompt.ask("course url", console=console).strip().split("/")[-1]

    if not _check_course(course_url, sessionid):
        console.print(
            Panel(
                Text("you have to buy the course first", style="bold red"),
                border_style="red",
            )
        )
        return 0

    chapters = _get_course_chapters(course_url)
    unit_links = _get_unit_links(course_url, chapters)
    total = len(unit_links)

    with open(str(Path.cwd() / f"{course_url}.txt"), "a", encoding="utf-8") as file:
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            TextColumn("[blue]{task.completed}/{task.total}"),
            console=console,
        ) as progress:
            task = progress.add_task("Processing...", total=total)
            for video_link in _get_video_links(unit_links):
                file.write(f"{video_link}\n")
                progress.update(task, advance=1)
                time.sleep(0.2)
    console.print(
        Panel(
            Text("✅ your file is valid until the next hour", style="bold yellow"),
            border_style="green",
        )
    )
    return 1


def schedule_download(sessionid):
    course_url = Prompt.ask("course url", console=console).strip().split("/")[-1]
    hours = [f"{i:02d}" for i in range(24)]
    minutes = [f"{i:02d}" for i in range(0, 60, 5)]

    console.print("🕐 [bold blue]Select your download time[/bold blue]")
    hour = inquirer.select(
        message="Choose hour:",
        choices=hours,
        default="00",
    ).execute()
    minute = inquirer.select(
        message="Choose minutes:",
        choices=minutes,
        default="00",
    ).execute()

    console.print(f"[bold green]Download scheduled for {hour}:{minute}[/bold green]")

    now = datetime.now()
    target_time = now.replace(
        hour=int(hour), minute=int(minute), second=0, microsecond=0
    )
    if target_time <= now:
        target_time += timedelta(days=1)

    with Live(console=console, refresh_per_second=1) as live:
        while True:
            now = datetime.now()

            if now >= target_time:
                break

            remaining = target_time - now
            total_seconds = int(remaining.total_seconds())
            hours_left, remainder = divmod(total_seconds, 3600)
            minutes_left, seconds_left = divmod(remainder, 60)

            text = Text()
            text.append("⏰ ", style="yellow bold")
            text.append("Time left: ", style="white bold")

            if hours_left > 0:
                text.append(f"{hours_left:02d}h ", style="cyan bold")
            if minutes_left > 0:
                text.append(f"{minutes_left:02d}m ", style="magenta bold")
            if hours_left == 0 and minutes_left == 0 and seconds_left > 0:
                text.append(f"{seconds_left:02d}s", style="magenta bold")

            live.update(text)

            if total_seconds > 60:
                sleep_duration = min(60, total_seconds - 60)
            else:
                sleep_duration = 1

    console.print(
        "[bold green]scheduled time reached! Starting download...[/bold green]"
    )
    return start_download(sessionid, course_url=course_url)
