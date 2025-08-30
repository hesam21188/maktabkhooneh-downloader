import os
import platform
import glob
from pathlib import Path
import browser_cookie3
from InquirerPy.base.control import Choice
from InquirerPy import inquirer


def _find_browser_paths():
    system = platform.system()
    home = Path.home()
    paths = {}

    if system == "Windows":
        paths = {
            "chrome": [
                home / "AppData/Local/Google/Chrome/User Data",
                home / "AppData/Local/Chromium/User Data",
            ],
            "firefox": [home / "AppData/Roaming/Mozilla/Firefox/Profiles"],
            "edge": [home / "AppData/Local/Microsoft/Edge/User Data"],
            "opera": [
                home / "AppData/Roaming/Opera Software/Opera Stable",
                home / "AppData/Local/Opera Software/Opera Stable",
            ],
            "opera_gx": [
                home / "AppData/Roaming/Opera Software/Opera GX Stable",
                home / "AppData/Local/Opera Software/Opera GX Stable",
            ],
            "brave": [home / "AppData/Local/BraveSoftware/Brave-Browser/User Data"],
            "vivaldi": [home / "AppData/Local/Vivaldi/User Data"],
        }
    elif system == "Darwin":  # macOS
        paths = {
            "chrome": [
                home / "Library/Application Support/Google/Chrome",
                home / "Library/Application Support/Chromium",
            ],
            "firefox": [home / "Library/Application Support/Firefox/Profiles"],
            "safari": [home / "Library/Cookies"],
            "edge": [home / "Library/Application Support/Microsoft Edge"],
            "opera": [home / "Library/Application Support/com.operasoftware.Opera"],
            "opera_gx": [
                home / "Library/Application Support/com.operasoftware.OperaGX"
            ],
            "brave": [home / "Library/Application Support/BraveSoftware/Brave-Browser"],
            "vivaldi": [home / "Library/Application Support/Vivaldi"],
        }
    else:  # Linux
        paths = {
            "chrome": [home / ".config/google-chrome", home / ".config/chromium"],
            "firefox": [home / ".mozilla/firefox"],
            "opera": [home / ".config/opera"],
            "opera_gx": [home / ".config/opera-gx"],
            "brave": [home / ".config/BraveSoftware/Brave-Browser"],
            "vivaldi": [home / ".config/vivaldi"],
        }

    found_browsers = {}
    for browser, browser_paths in paths.items():
        for path in browser_paths:
            if path.exists():
                found_browsers[browser] = path
                break
    return found_browsers


def _find_cookie_files(browser_path, browser_name):
    cookie_files = []

    if browser_name in [
        "chrome",
        "edge",
        "opera",
        "opera_gx",
        "brave",
        "vivaldi",
        "chromium",
    ]:
        patterns = [
            browser_path / "Default/Cookies",
            browser_path / "Default/Network/Cookies",
            browser_path / "Profile*/Cookies",
            browser_path / "Profile*/Network/Cookies",
        ]
        for pattern in patterns:
            if pattern.exists():
                cookie_files.append(pattern)
            else:
                cookie_files.extend(Path(f) for f in glob.glob(str(pattern)))

    elif browser_name == "firefox":
        for profile_dir in glob.glob(str(browser_path / "*.default*")):
            cookie_db = Path(profile_dir) / "cookies.sqlite"
            if cookie_db.exists():
                cookie_files.append(cookie_db)

    elif browser_name == "safari":
        cookie_file = browser_path / "Cookies.binarycookies"
        if cookie_file.exists():
            cookie_files.append(cookie_file)

    return cookie_files


def _extract_sessionid_cookie(cookie_file, browser_name):
    domain = "maktabkhooneh.org"
    cookie_extractors = {
        "chrome": browser_cookie3.chrome,
        "chromium": browser_cookie3.chrome,
        "firefox": browser_cookie3.firefox,
        "edge": browser_cookie3.edge,
        "opera": browser_cookie3.opera,
        "opera_gx": browser_cookie3.opera_gx,
        "brave": browser_cookie3.brave,
        "vivaldi": browser_cookie3.vivaldi,
        "safari": browser_cookie3.safari,
    }

    # Try extracting from specific file
    extractor = cookie_extractors.get(browser_name, browser_cookie3.chrome)
    try:
        cj = extractor(cookie_file=str(cookie_file), domain_name=domain)
        for cookie in cj:
            if cookie.name == "sessionid" and domain in cookie.domain:
                return cookie.value
    except Exception:
        pass

    # Fallback: try without specifying file
    try:
        cj = extractor(domain_name=domain)
        for cookie in cj:
            if cookie.name == "sessionid" and domain in cookie.domain:
                return cookie.value
    except Exception:
        pass

    # Final fallback to chrome if all else fails
    try:
        cj = browser_cookie3.chrome(domain_name=domain)
        for cookie in cj:
            if cookie.name == "sessionid" and domain in cookie.domain:
                return cookie.value
    except Exception:
        pass

    return None


def _get_sessionid_cookies():
    result = {}
    browsers = _find_browser_paths()

    for browser_name, browser_path in browsers.items():
        cookie_files = _find_cookie_files(browser_path, browser_name)
        for cookie_file in cookie_files:
            sessionid = _extract_sessionid_cookie(cookie_file, browser_name)
            if sessionid:
                result[browser_name] = sessionid
                break

    return result


def get_sessionid():
    sessionids = _get_sessionid_cookies()
    if len(sessionids) > 1:
        choices = []
        for key, value in sessionids.items():
            choices.append(Choice(value=value, name=key))

        choice = inquirer.select(
            message="Select a browser for login:", choices=choices
        ).execute()
        return choice
    return list(sessionids.values())[0]
