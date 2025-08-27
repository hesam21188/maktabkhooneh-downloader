from codecs import charmap_build
import time
from InquirerPy import base
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
    TransferSpeedColumn,
    TimeRemainingColumn,
)
import os

console = Console()
session = requests.Session()


def check_course(url, sessionid):
    base_url = f"https://maktabkhooneh.org/api/v1/sale/{url}/prices"
    session.cookies.set("sessionid", sessionid)
    r = session.get(base_url)
    if r.status_code == 200:
        if not json.loads(r.text)["can_purchase"]["CONTENT"]:
            return True
    return False


def get_course_chapters(url):
    base_url = f"https://maktabkhooneh.org/api/v1/courses/{url}/chapters/"
    r = session.get(base_url)
    if r.status_code == 200:
        data = json.loads(r.text)
        chapters = {}
        for chapter in data["chapters"]:
            chapters[f"{chapter["slug"]}-ch{chapter["id"]}"] = [
                unit["slug"] for unit in chapter["unit_set"]
            ]

        return chapters


def get_unit_links(url, chapters):
    base_url = f"https://maktabkhooneh.org/course/{url}"
    unit_links = []
    for chapter in chapters:
        for unit in chapters[chapter]:
            unit_links.append(f"{base_url}/{chapter}/{unit}")
    return unit_links


def get_video_links(unit_links, high_quality=True):
    for unit in unit_links:
        r = session.get(unit)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "html.parser")
            if high_quality:
                yield soup.find_all(
                    "a",
                    attrs={"onclick": lambda x: x and "send_download_event(1)" in x},
                )[0]["href"]
            else:
                yield soup.find_all(
                    "a",
                    attrs={"onclick": lambda x: x and "send_download_event(0)" in x},
                )[0]["href"]


def download_video(url, filepath):
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


def start_download(sessionid):
    course_url = Prompt.ask("course url", console=console).strip().split("/")[-1]
    if not check_course(course_url, sessionid):
        console.print(
            Panel(
                Text("you have to buy the course first", style="bold red"),
                border_style="red",
            )
        )
        return 0
    chapters = get_course_chapters(course_url)
    unit_links = get_unit_links(course_url, chapters)

    for i, video_link in enumerate(get_video_links(unit_links)):
        file_name = unit_links[i].split("/")[-2:]
        file_name[0] = "-".join(file_name[0].split("-")[:-1])
        file_name[1:1] = ["/"]
        file_name.append(".mp4")
        file_name = "".join(file_name)
        download_video(video_link, file_name)

    return 1


# {
#     "فصل-اول-مقدمه": ["ویدیو-مقدمه"],
#     "فصل-دوم-آزمایشگاه": [
#         "ویدیو-ماشین-مجازی",
#         "ویدیو-نصب-سیستم-عامل-کالی",
#         "ویدیو-metasploitable",
#         "ویدیو-owaspbwa",
#     ],
#     "فصل-سوم-اصطلاحات-ceh": [
#         "ویدیو-اصطلاحات-هک-اخلاقی",
#         "ویدیو-اصطلاحات-امنیت-اطلاعات",
#         "ویدیو-اصطلاحات-حمله",
#         "ویدیو-مراحل-هک",
#         "ویدیو-اخبار-بارهی-هک",
#         "ویدیو-مبانی-هک",
#         "تمرین-کوییز",
#     ],
#     "فصل-چهارم-بررسی-شناسایی-درپاها": [
#         "ویدیو-مقدمه-پیدا-کردن-ردپا",
#         "ویدیو-هک-گوگل",
#         "ویدیو-مهندسی-اجتماعی",
#         "ویدیو-بررسی-وبسات",
#         "ویدیو-هدر-ایمیل",
#         "ویدیو-dns",
#         "تمرین-کوییز",
#         "پروژه-پروژه",
#     ],
#     "فصل-پنجم-اسکن-سیستماتیک-شبکه": [
#         "ویدیو-مقدمه-اسکن-سیستماتیک",
#         "ویدیو-مبانی-اسکن-پورتها",
#         "ویدیو-hping3",
#         "ویدیو-nmap",
#         "ویدیو-idle",
#         "ویدیو-پیدا-کردن-ردپا",
#         "ویدیو-nessus",
#         "ویدیو-solar-network-mapper",
#         "ویدیو-scapy",
#         "ویدیو-proxies",
#         "تمرین-کوییز",
#     ],
#     "فصل-ششم-سرشماری": [
#         "ویدیو-مقدمه-سرشماری",
#         "ویدیو-windows",
#         "ویدیو-linux",
#         "ویدیو-netbios",
#         "ویدیو-dns",
#         "ویدیو-snmp",
#         "ویدیو-idap",
#         "ویدیو-ntp",
#         "ویدیو-smtp",
#         "تمرین-کوییز",
#     ],
#     "فصل-هفتم-هک-کردن-سیستم": [
#         "ویدیو-مقدمه-هک-کردن-سیستم",
#         "ویدیو-رمزعبور-قسمت-1",
#         "ویدیو-رمزعبور-قسمت-۲",
#         "ویدیو-رمزعبور-قسمت-۳",
#         "ویدیو-رمزعبور-قسمت-4",
#         "ویدیو-اجرا",
#         "ویدیو-بالا-بردن-دسترسی-privilege-escalation",
#         "ویدیو-مسیرهای-مخفی",
#         "ویدیو-دادههای-مخفی",
#         "ویدیو-msfvenom-backdoor",
#         "ویدیو-yersinia",
#         "تمرین-کوییز",
#         "پروژه-پروژه",
#     ],
#     "فصل-هشتم-بدافزار": [
#         "ویدیو-مقدمه-بدافزار",
#         "ویدیو-جاسوسافزار",
#         "ویدیو-تروجان",
#         "ویدیو-ویروس",
#         "ویدیو-تشخیص",
#         "ویدیو-چرخه",
#         "ویدیو-تایید-فایل",
#         "ویدیو-آنالیز",
#         "ویدیو-سرریز-بافر",
#         "تمرین-کوییز",
#     ],
#     "فصل-نهم-شنود": [
#         "ویدیو-مقدمه-شنود",
#         "ویدیو-tcpdump-wireshark",
#         "ویدیو-cam",
#         "ویدیو-dhcp-snooping",
#         "ویدیو-arp",
#         "تمرین-کوییز",
#         "پروژه-پروژه",
#     ],
#     "فصل-دهم-مهندسی-اجتماعی": [
#         "ویدیو-مقدمه-مهندسی-اجتماعی",
#         "ویدیو-فازهای-مهندسی-اجتماعی",
#         "ویدیو-حمله",
#         "ویدیو-جلوگیری",
#         "تمرین-کوییز",
#     ],
#     "فصل-یازدهم-dos": [
#         "ویدیو-مقدمه-dos",
#         "ویدیو-لایههای-dos",
#         "ویدیو-hping3",
#         "ویدیو-جلوگیری",
#         "تمرین-کوییز",
#     ],
#     "فصل-دوازدهم-نشست-ربایی": [
#         "ویدیو-مقدمه-لایههای-شبکه",
#         "ویدیو-لایههای-برنامه",
#         "ویدیو-جلوگیری",
#         "تمرین-کوییز",
#     ],
#     "فصل-سیزدهم-سرورها-برنامه-وب": [
#         "ویدیو-مقدمه-سرورها-برنامههای-وب",
#         "ویدیو-حمله",
#         "ویدیو-handson",
#         "تمرین-کوییز",
#     ],
#     "فصل-چهاردهم-تزریق-پایگاه-داده": [
#         "ویدیو-مقدمه-تزریق-پایگاهداده",
#         "ویدیو-حمله",
#         "ویدیو-ابزارهای-جلوگیری",
#         "ویدیو-handson",
#         "تمرین-کوییز",
#         "پروژه-پروژه",
#     ],
#     "فصل-پانزدهم-امنیت-wifi": [
#         "ویدیو-مقدمه-امنیت-wifi",
#         "ویدیو-jargon",
#         "ویدیو-waves",
#         "ویدیو-استانداردها-مقررات",
#         "ویدیو-hidden-ssid",
#         "ویدیو-mac-filter",
#         "ویدیو-wpa2-cracking",
#         "ویدیو-rouge",
#         "ویدیو-miss-association-evil-twin",
#         "ویدیو-bt-mobile",
#         "ویدیو-دفاع",
#         "تمرین-کوییز",
#         "پروژه-پروژه",
#     ],
#     "فصل-شانزدهم-دستگاههای-قابل-حمل": ["ویدیو-toward", "ویدیو-دفاع", "تمرین-کوییز"],
#     "فصل-هفدهم-گریز": [
#         "ویدیو-مقدمه-ابزارها",
#         "ویدیو-honeypots",
#         "ویدیو-تکنیکهای-فرار",
#         "تمرین-کوییز",
#     ],
#     "فصل-هجدهم-ابر": ["ویدیو-مقدمه-ابر", "ویدیو-نگرانیها", "تمرین-کوییز"],
#     "فصل-نوزدهم-رمزنگاری": [
#         "ویدیو-مقدمه-رمزنگاری",
#         "ویدیو-اصول-رمزنگاری",
#         "ویدیو-symmetric",
#         "ویدیو-asymmetric",
#         "ویدیو-cas",
#         "ویدیو-hashes",
#         "تمرین-کوییز",
#         "پروژه-پروژه",
#     ],
#     "فصل-بیستم-امنیت-فیزیکی": ["ویدیو-امنیت-فیزیکی", "تمرین-کوییز"],
#     "فصل-بیست-یکم-معماری-طراحی-امنیتی": [
#         "ویدیو-چارت-سازمانی",
#         "ویدیو-معماری-برنامه",
#         "تمرین-کوییز",
#     ],
#     "فصل-بیست-دوم-اینترنت-اشیا": [
#         "ویدیو-اینترنت-اشیا",
#         "ویدیو-ادامه-آموزش",
#         "تمرین-کوییز",
#     ],
# }
