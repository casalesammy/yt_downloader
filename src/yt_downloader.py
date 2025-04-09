import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from PIL import Image, ImageTk
import subprocess
import threading
import urllib.request
import io

def browse_folder():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        folder_path.set(folder_selected)

def fetch_title_and_thumbnail(event=None):
    url = url_entry.get().strip()
    if not url:
        video_title.set("")
        thumbnail_label.config(image="")
        return
    try:
        # Get title
        title_result = subprocess.run(["yt-dlp", "--get-title", url], capture_output=True, text=True, check=True)
        title = title_result.stdout.strip()
        video_title.set(f"🎵 Title: {title}")

        # Get thumbnail URL
        thumb_result = subprocess.run(["yt-dlp", "--get-thumbnail", url], capture_output=True, text=True, check=True)
        thumbnail_url = thumb_result.stdout.strip()

        # Download and show image
        image_bytes = urllib.request.urlopen(thumbnail_url).read()
        image = Image.open(io.BytesIO(image_bytes))
        image.thumbnail((320, 180))  # Resize to fit GUI
        photo = ImageTk.PhotoImage(image)

        thumbnail_label.config(image=photo)
        thumbnail_label.image = photo  # Keep reference to avoid garbage collection
    except:
        video_title.set("⚠️ Could not fetch title")
        thumbnail_label.config(image="")

def get_format_string(quality):
    if quality == "360p":
        return "best[height<=360]"
    elif quality == "480p":
        return "best[height<=480]"
    elif quality == "720p":
        return "best[height<=720]"
    else:
        return "best"

def run_download():
    url = url_entry.get().strip()
    save_path = folder_path.get().strip()
    quality = quality_var.get()

    try:
        status_label.config(text="Downloading...", foreground="blue")
        progress.start(10)

        format_str = get_format_string(quality)

        command = ["yt-dlp", "-f", format_str, "-P", save_path, url]
        subprocess.run(command, check=True)

        progress.stop()
        status_label.config(text="✅ Download complete!", foreground="green")
    except subprocess.CalledProcessError:
        progress.stop()
        status_label.config(text="❌ Download failed!", foreground="red")
    except Exception as e:
        progress.stop()
        messagebox.showerror("Error", str(e))
        status_label.config(text="❌ Error occurred.", foreground="red")

def start_download_thread():
    url = url_entry.get().strip()
    save_path = folder_path.get().strip()

    if not url:
        messagebox.showwarning("Input Error", "Please paste a YouTube URL.")
        return
    if not save_path:
        messagebox.showwarning("Input Error", "Please choose a download folder.")
        return

    download_thread = threading.Thread(target=run_download)
    download_thread.start()

# GUI setup
root = tk.Tk()
root.title("📥 YouTube Downloader with Preview")
root.geometry("550x500")
root.resizable(False, False)
root.configure(bg="#f2f2f2")

style = ttk.Style()
style.configure("TButton", font=("Segoe UI", 10), padding=6)
style.configure("TLabel", font=("Segoe UI", 10), background="#f2f2f2")

# Link input
ttk.Label(root, text="Paste a YouTube video link below:").pack(pady=(15, 5))
url_entry = tk.Entry(root, width=60, font=("Segoe UI", 10))
url_entry.pack(pady=5, ipady=5)
url_entry.bind("<FocusOut>", fetch_title_and_thumbnail)

# Video title
video_title = tk.StringVar()
ttk.Label(root, textvariable=video_title, font=("Segoe UI", 9, "italic")).pack()

# Thumbnail display
thumbnail_label = tk.Label(root, bg="#f2f2f2")
thumbnail_label.pack(pady=10)

# Quality selector
ttk.Label(root, text="Choose Quality:").pack(pady=(0, 0))
quality_var = tk.StringVar(value="480p")
quality_menu = ttk.Combobox(root, textvariable=quality_var, values=["360p", "480p", "720p", "Best"], state="readonly")
quality_menu.pack(pady=5)

# Folder selection
folder_path = tk.StringVar()
folder_frame = tk.Frame(root, bg="#f2f2f2")
folder_frame.pack(pady=(10, 5))

folder_entry = tk.Entry(folder_frame, textvariable=folder_path, width=42, font=("Segoe UI", 10))
folder_entry.pack(side=tk.LEFT, padx=5, ipady=4)

ttk.Button(folder_frame, text="📁 Browse", command=browse_folder).pack(side=tk.LEFT)

# Download button
ttk.Button(root, text="🎬 Download Video", command=start_download_thread).pack(pady=15)

# Progress bar
progress = ttk.Progressbar(root, orient="horizontal", length=300, mode="indeterminate")
progress.pack(pady=(5, 5))

# Status label
status_label = ttk.Label(root, text="", font=("Segoe UI", 10, "italic"))
status_label.pack()

root.mainloop()
