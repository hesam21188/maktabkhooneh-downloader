## maktabkhooneh-downloader ✨

[Persian README (فارسی)](README_FA.md)

Effortlessly download your Maktabkhooneh courses with a friendly, interactive CLI — built for speed, reliability, and convenience. 🚀
Enjoy a delightful, menu-driven experience with colorful prompts and clear steps. 🧭🎛️

---

⚠️ Important — Legal & Ethics

- This tool works only for courses you are allowed to download. ✅
- Use it solely for your own content and obey the platform’s Terms of Service. 🙏
- The authors are not responsible for misuse.

---

### Features at a glance

- 💨 Instant video downloads
- ⏰ Scheduled downloading (download later automatically)
- 🧾 Export a `.txt` file of all downloadable links
- 👤 Manual login
- 🤖 Automatic login via browser cookies
- 🔁 Resume incomplete/failed downloads
- 🌈 Rich, interactive CLI menus

---

### Quick Install

The easiest way is via pip (provides the `mkdl` command):

```bash
pip install mkdl
```

Or upgrade to the latest version:

```bash
pip install -U mkdl
```

Minimum Python version: 3.11

---

### Manual Install (Poetry) 🛠️

First, ensure Poetry is installed. If not, install it with:

```bash
pip install poetry
```

```bash
git clone https://github.com/hesam21188/maktabkhooneh-downloader.git
cd maktabkhooneh-downloader
poetry install --no-interaction
poetry run mkdl
```

---

### Usage

- Recommended (installed via pip):

```bash
mkdl
```

- Alternative (module mode):

```bash
poetry run mkdl
```

You’ll get interactive menus exactly like these:

- Login menu:

  - 🔥 Auto login (from your browser cookies)
  - ⚡ Manual login (enter your session id manually)
  - 🚪 Exit

- Download menu (after login):
  - start download 🚀
  - schedule download ⏰
  - get txt file of video links (for IDM) 📥
  - change (login again) 🔄
  - 🚪 Exit

---

### Examples

- Start the interactive app and pick what you need from the menus:

```bash
mkdl
```

- Example flows you can select from the menus:
  - 🎬 Instant download: Choose a course and start downloading right away
  - ⏱️ Scheduled download: Set a time and let it download later automatically
  - 🧾 Export links: Generate a `.txt` containing all downloadable URLs
  - 🔁 Resume: Continue an incomplete/failed download from where it stopped

---

### How login works 🔐

- Automatic login extracts your existing session from supported browsers (when possible)
- If automatic login fails, switch to manual login from the menu
- If you’re logged in on multiple browsers, you can choose which browser profile to use

---

### Troubleshooting 🧰

- If automatic login doesn’t work, try manual login from the menu
- If a download stops midway, simply run the tool again — it resumes where it left off
- Ensure you have permission to download the course (the tool won’t bypass restrictions)
- Use Python 3.11+ and keep `mkdl` updated: `pip install -U mkdl`

---

### Uninstall

```bash
pip uninstall mkdl
```

---

### Contributing 🤝

PRs and suggestions are welcome! Please follow conventional best practices and keep the UX friendly.

---

### License

Distributed under the GNU General Public License (GPL). See `LICENSE` for details.
