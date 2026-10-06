# Contributing to YouTube Downloader Pro

Thank you for your interest in contributing to **YouTube Downloader Pro**! 🎉

## How to Contribute

1. **Fork the Repository**:
   Click the "Fork" button at the top right of the GitHub page.

2. **Clone your Fork**:
   ```bash
   git clone https://github.com/justyadav/youtube-downloader-pro.git
   cd youtube-downloader-pro
   ```

3. **Create a Feature Branch**:
   ```bash
   git checkout -b feature/amazing-feature
   ```

4. **Install Dependencies**:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Linux/macOS:
   source venv/bin/activate

   pip install -r requirements.txt
   ```

5. **Make your changes and verify**:
   Ensure both Web GUI (`server.py`) and CLI (`downloader_cli.py`) work properly.
   Run:
   ```bash
   python -c "import downloader_core, server, downloader_cli; print('All ok')"
   ```

6. **Commit & Push**:
   ```bash
   git commit -m "feat: add support for new feature"
   git push origin feature/amazing-feature
   ```

7. **Open a Pull Request**:
   Submit your pull request describing the changes and testing performed.
