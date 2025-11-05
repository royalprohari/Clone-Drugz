import subprocess
import time
import datetime
import os
import sys
import glob

# Path to your bot's main file
BOT_MAIN_FILE = "__main__.py"
REQUIREMENTS_FILE = "requirements.txt"
RESTART_DELAY = 60  # seconds between restarts

LOG_FILE = "autorestart.log"
restart_count = 0


def log(message: str):
    """Log messages with timestamp to console and file."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg = f"[{timestamp}] {message}"
    print(msg)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(msg + "\n")


def remove_session_files():
    """Delete all .session and .session-journal files in the current directory."""
    patterns = ["*.session", "*.session-journal"]
    removed_any = False
    for pattern in patterns:
        files = glob.glob(pattern)
        if files:
            removed_any = True
            for file in files:
                try:
                    os.remove(file)
                    log(f"🗑️ Removed file: {file}")
                except Exception as e:
                    log(f"❌ Failed to remove {file}: {e}")
    if not removed_any:
        log("⚠️ No .session or .session-journal files found — nothing to remove.")


def install_requirements():
    """Install dependencies from requirements.txt if it exists."""
    remove_session_files()  # Remove session files before installing requirements

    if os.path.exists(REQUIREMENTS_FILE):
        log("Installing dependencies from requirements.txt...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", REQUIREMENTS_FILE])
            log("✅ Requirements installed successfully.")
        except subprocess.CalledProcessError as e:
            log(f"❌ Error installing requirements: {e}")
    else:
        log("⚠️ No requirements.txt found — skipping dependency installation.")


def start_bot():
    """Start the bot process and wait for it to finish."""
    global restart_count
    restart_count += 1
    log(f"Starting bot process (Restart #{restart_count})...")
    process = subprocess.Popen([sys.executable, BOT_MAIN_FILE])
    process.wait()
    exit_code = process.returncode
    log(f"💥 Bot stopped (exit code: {exit_code}).")
    return exit_code


def autorestart():
    """Continuously restart the bot if it stops."""
    install_requirements()  # Install before first run
    while True:
        exit_code = start_bot()
        log(f"🔁 Restarting in {RESTART_DELAY} seconds...")
        time.sleep(RESTART_DELAY)
        install_requirements()  # Install before next restart
