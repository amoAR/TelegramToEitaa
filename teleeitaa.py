import os
import sys
import time
import datetime
import mimetypes
import tempfile
import asyncio
from pyrogram import Client
from colorama import Fore, Style
from eitaa import Eitaa

# Telegram API credentials
API_ID = ""
API_HASH = ""

# Eitaa API credentials
TOKEN = ""
CHAT_ID = ""

# Proxy configuration
PROXY = {
    "hostname": "",
    "port": 0,
    "scheme": "",
}

# Temporary directory for downloads
DOWNLOAD_DIR = tempfile.TemporaryDirectory(prefix="TeleEitaa_", ignore_cleanup_errors=True)

# ASCII art and tagline
ASCII_ART = r"""
████████╗███████╗██╗     ███████╗███████╗██╗████████╗ ███╗    ███╗  
╚══██╔══╝██╔════╝██║     ██╔════╝██╔════╝██║╚══██╔══╝██╔██╗  ██╔██╗ 
   ██║   █████╗  ██║     █████╗  █████╗  ██║   ██║  ███████║███████║
   ██║   ██╔══╝  ██║     ██╔══╝  ██╔══╝  ██║   ██║  ██╔══██║██╔══██║
   ██║   ███████╗███████╗███████║███████║██║   ██║  ██║  ██║██║  ██║
   ╚═╝   ╚══════╝╚══════╝╚══════╝╚══════╝╚═╝   ╚═╝  ╚═╝  ╚═╝╚═╝  ╚═╝
                            TeleEitaa
"""
TAGLINE = "\t\tTelegram media to Eitaa \033[4meffortlessly\033[0m"

# Function to display the startup screen
def show_startup():
    print("\n")
    print(Fore.CYAN + ASCII_ART + Style.RESET_ALL)
    print(Fore.GREEN + TAGLINE + Style.RESET_ALL)
    time.sleep(2)

# Function to show the download directory message
def show_download_message():
    message = f"\n\n\n{Fore.CYAN}🚀 Temporary session initialized at:{Style.RESET_ALL}"
    for char in message:
        print(char, end="", flush=True)
        time.sleep(0.03)
    print(f" {Fore.YELLOW}{Style.BRIGHT}{DOWNLOAD_DIR.name}{Style.RESET_ALL}\n")

# Function to show a progress bar during downloads
async def show_progress(current, total):
    bar_length = 30
    filled_length = int(bar_length * current / total)
    bar = "#" * filled_length + "-" * (bar_length - filled_length)
    percent = current * 100 / total
    sys.stdout.write(f"\r[{bar}] {percent:.1f}%")
    sys.stdout.flush()

# Main function to download media from Telegram
async def download_from_telegram() -> None:
    async with Client("tdl_session", API_ID, API_HASH, proxy=PROXY) as app:
        async for message in app.get_chat_history("me"):
            if not message.media:
                continue

            # Determine the file extension
            file_id, extension = None, None
            if message.photo:
                file_id, extension = message.photo.file_id, "jpg"
            elif message.video:
                file_id, extension = message.video.file_id, "mp4"
            elif message.document:
                file_id, extension = message.document.file_id, "temp"
            elif message.audio:
                file_id, extension = message.audio.file_id, "ogg"
            else:
                continue

            file_path = os.path.join(DOWNLOAD_DIR.name, f"{file_id}.{extension}")
            
            try:
                downloaded_path = await app.download_media(
                    message, file_name=file_path, progress=show_progress
                )
            except Exception as e:
                print(f"{Fore.RED}Error downloading media:{Style.RESET_ALL} {e}")
                exit() #todo

            # Rename file if needed
            if extension == "temp":
                mime_extension = mimetypes.guess_extension(message.document.mime_type)
                if mime_extension:
                    new_file_path = os.path.splitext(file_path)[0] + mime_extension
                    os.rename(file_path, new_file_path)
                    file_path = new_file_path

            print(f"\t{Fore.GREEN}Completed!{Style.RESET_ALL}\t...\\...\\{file_path[-11:]}")

# Function to send files to Eitaa
def send_to_eitaa() -> None:
    print("\n")
    print("📤 Sending medias to Eitaa...", end="", flush=True)
    eitaa = Eitaa(TOKEN)
    for file in os.scandir(DOWNLOAD_DIR.name):
        if file.is_file():
            try:
                response = eitaa.send_file(
                    chat_id=CHAT_ID,
                    caption=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    file=file.path,
                    disable_notification=True,
                )
                if response.get("ok", False):
                    pass
                else:
                    print(f"{Fore.RED}Failed to send {file.name}: {response}{Style.RESET_ALL}")
                    exit()
            except Exception as e:
                print(f"{Fore.RED}Error sending {file.name}:{Style.RESET_ALL} {e}")
    time.sleep(2)
    print("\r" + " " * 30, end="", flush=True)  # Clears the previous line
    print("\r✅ Files sent to Eitaa successfully.")

# Main entry point
if __name__ == "__main__":
    show_startup()
    show_download_message()

    try:
        # Run download and send functions
        asyncio.run(download_from_telegram())
        send_to_eitaa()
    except Exception as e:
        print(f"{Fore.RED}Error:{Style.RESET_ALL} {e}")
    finally:
        # Cleanup and exit
        if DOWNLOAD_DIR:
            DOWNLOAD_DIR.cleanup()
        print("\n⌛ Ending temporary session...", end=" ")
        time.sleep(1.5)
        print(f"\t{Fore.MAGENTA}Goodbye!{Style.RESET_ALL}\n")
        input(f"{Fore.YELLOW}Press the <ENTER> key to exit...{Style.RESET_ALL}")