import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from ttkthemes import ThemedTk
import requests
from PIL import Image
from io import BytesIO
import os
from pathlib import Path
import threading
import urllib.parse

# --- Configuration ---
APP_TITLE = "WebP URL to PNG Converter"
THEME_NAME = "equilux" # Or try 'black', 'adapta', etc.
CREDITS = "by @DangerousPixel"

# --- Core Logic ---

def find_downloads_folder():
    """Finds the user's Downloads folder."""
    return Path.home() / "Downloads"

def get_output_filename(url):
    """Generates a PNG filename based on the URL."""
    try:
        parsed_url = urllib.parse.urlparse(url)
        # Get the last part of the path
        base_name = os.path.basename(parsed_url.path)
        # Remove query string influence if basename is empty
        if not base_name and parsed_url.path:
             base_name = parsed_url.path.strip('/').split('/')[-1]

        # Remove original extension (if any)
        name_without_ext, _ = os.path.splitext(base_name)

        # Handle empty or default names
        if not name_without_ext or name_without_ext in ['index', 'image', 'download']:
             # Try using a part of the query string if path is unhelpful
             query_parts = urllib.parse.parse_qs(parsed_url.query)
             if query_parts:
                 # Heuristic: use the first key/value pair or 'image'
                 first_key = next(iter(query_parts))
                 name_without_ext = f"{first_key}_{query_parts[first_key][0]}"
             else:
                 name_without_ext = "converted_image" # Fallback

        # Sanitize filename (basic)
        safe_name = "".join(c for c in name_without_ext if c.isalnum() or c in ('_', '-')).rstrip()
        if not safe_name:
            safe_name = "converted_image" # Final fallback

        return f"{safe_name}.png"
    except Exception:
        # Fallback if URL parsing fails unexpectedly
        return "converted_image.png"


def process_urls(urls, status_callback, progress_callback, completion_callback):
    """Downloads, converts, and saves images from a list of URLs."""
    downloads_folder = find_downloads_folder()
    try:
        if not downloads_folder.exists():
            downloads_folder.mkdir(parents=True)
        status_callback(f"Saving to: {downloads_folder}")
    except OSError as e:
        status_callback(f"Error creating Downloads folder: {e}")
        completion_callback(success=False, message="Failed to access Downloads folder.")
        return

    total_urls = len(urls)
    success_count = 0
    errors = []

    for i, url in enumerate(urls):
        progress_callback(i + 1, total_urls, url)
        output_filename = get_output_filename(url)
        output_path = downloads_folder / output_filename

        # Handle potential filename conflicts by adding a number
        counter = 1
        original_output_path = output_path
        while output_path.exists():
            name, ext = os.path.splitext(original_output_path.name)
            # Remove previous counter if exists (e.g., image_1 -> image_2, not image_1_2)
            if name.endswith(f"_{counter-1}"):
                 name = name[:-len(f"_{counter-1}")]
            output_filename = f"{name}_{counter}{ext}"
            output_path = downloads_folder / output_filename
            counter += 1
            if counter > 100: # Safety break
                errors.append(f"Too many conflicts for base name: {original_output_path.stem}")
                break
        if output_path.exists(): # Skip if safety break triggered
             continue

        try:
            status_callback(f"[{i+1}/{total_urls}] Downloading: {url[:50]}...")
            response = requests.get(url, stream=True, timeout=30) # Added timeout
            response.raise_for_status() # Check for HTTP errors

            # Check content type (optional but good practice)
            content_type = response.headers.get('content-type', '').lower()
            if 'image' not in content_type:
                 print(f"Warning: URL {url} Content-Type is '{content_type}', trying to open anyway.")
                 # errors.append(f"URL is not an image ({content_type}): {url[:50]}...")
                 # continue # Or be strict and skip

            status_callback(f"[{i+1}/{total_urls}] Converting...")
            img_data = BytesIO(response.content) # Read content into memory
            with Image.open(img_data) as img:
                # Ensure image mode is suitable for PNG (e.g., handle palette)
                if img.mode == 'P':
                    img = img.convert('RGBA')
                elif img.mode == 'RGB':
                     img = img.convert('RGBA') # Add alpha for consistency if needed

                status_callback(f"[{i+1}/{total_urls}] Saving as: {output_filename}")
                img.save(output_path, "PNG")
                success_count += 1

        except requests.exceptions.RequestException as e:
            error_msg = f"Network error for {url[:50]}...: {e}"
            print(error_msg)
            errors.append(error_msg)
        except Image.UnidentifiedImageError:
            error_msg = f"Cannot identify image file: {url[:50]}..."
            print(error_msg)
            errors.append(error_msg)
        except Exception as e:
            error_msg = f"Error processing {url[:50]}...: {e}"
            print(error_msg)
            errors.append(error_msg)

    completion_callback(success=(success_count > 0 or not errors),
                       message=f"Finished. {success_count}/{total_urls} converted.",
                       errors=errors)


# --- GUI Class ---

class App:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        # self.root.geometry("600x450") # Optional: set initial size

        # --- Style Configuration ---
        style = ttk.Style(self.root)
        # Custom Deep Blue Ocean Theme Colors
        DEEP_BLUE_BG = "#0a192f"
        OCEAN_DARK = "#112240"
        OCEAN_ACCENT = "#233554"
        OCEAN_BUTTON = "#1e3a5c"
        OCEAN_BUTTON_ACTIVE = "#2563eb"
        TEXT_COLOR = "#e0e6ed"
        ACCENT_COLOR = "#64ffda"
        ERROR_COLOR = "#ff5370"

        self.root.configure(bg=DEEP_BLUE_BG)
        style.theme_use("clam")
        style.configure("TFrame", background=DEEP_BLUE_BG)
        style.configure("TLabel", background=DEEP_BLUE_BG, foreground=TEXT_COLOR)
        style.configure("TButton", background=OCEAN_BUTTON, foreground=TEXT_COLOR, borderwidth=1, focusthickness=2, focuscolor=OCEAN_BUTTON_ACTIVE)
        style.map("TButton",
            background=[("active", OCEAN_BUTTON_ACTIVE), ("pressed", ACCENT_COLOR)],
            foreground=[("active", TEXT_COLOR), ("pressed", OCEAN_DARK)])
        style.configure("TEntry", fieldbackground=OCEAN_DARK, foreground=TEXT_COLOR)
        style.configure("TScrollbar", background=OCEAN_DARK, troughcolor=OCEAN_DARK)

        main_frame = ttk.Frame(self.root, padding="10 10 10 10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.configure(style="TFrame")

        # Input Label
        input_label = ttk.Label(main_frame, text="Links list :", style="TLabel")
        input_label.pack(pady=(0, 5), anchor="w")

        # Queue Listbox
        queue_label = ttk.Label(main_frame, text="Queue:", style="TLabel")
        queue_label.pack(anchor="w")
        self.queue_listbox = tk.Listbox(main_frame, height=7, width=60, bg=OCEAN_DARK, fg=TEXT_COLOR, selectbackground=OCEAN_ACCENT, selectforeground=DEEP_BLUE_BG, highlightbackground=OCEAN_ACCENT, relief=tk.FLAT, borderwidth=0)
        self.queue_listbox.pack(fill=tk.BOTH, expand=False, pady=(0,5))

        # Button Frame
        button_frame = ttk.Frame(main_frame, style="TFrame")
        button_frame.pack(fill=tk.X, pady=(5, 5))

        # Paste Button
        self.paste_button = ttk.Button(button_frame, text="Paste", command=self.paste_clipboard, style="TButton")
        self.paste_button.pack(side=tk.LEFT, padx=(0, 10))

        # Convert Button
        self.convert_button = ttk.Button(button_frame, text="Convert & Save PNGs", command=self.start_processing, style="TButton")
        self.convert_button.pack(side=tk.LEFT, padx=(0, 10))

        # Clear Queue Button
        self.clear_queue_button = ttk.Button(button_frame, text="Clear Queue", command=self.clear_queue, style="TButton")
        self.clear_queue_button.pack(side=tk.LEFT)

        # Status Label
        self.status_var = tk.StringVar()
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var, wraplength=550, style="TLabel")
        self.status_label.pack(pady=(5, 5), anchor="w")
        self.status_var.set("Ready.")

        # Internal queue storage
        self.url_queue = []

        # Button Frame for clear only
        button_frame2 = ttk.Frame(main_frame, style="TFrame")
        button_frame2.pack(fill=tk.X, pady=(10, 5))

        # Clear Button
        self.clear_button = ttk.Button(button_frame2, text="Clear", command=self.clear_fields, style="TButton")
        self.clear_button.pack(side=tk.LEFT)

        # Credits Label (only one at the bottom)
        credits_label = ttk.Label(main_frame, text=CREDITS, font=('TkDefaultFont', 8), style="TLabel")
        credits_label.pack(side=tk.BOTTOM, pady=(10, 0))

    def update_status(self, message):
        """Updates the status label safely from any thread."""
        self.root.after(0, self.status_var.set, message)

    def update_progress(self, current, total, url):
         """Updates status with progress information."""
         self.update_status(f"Processing [{current}/{total}]: {url[:60]}...")


    def clear_fields(self):
        """Clears the status label only."""
        self.status_var.set("Fields cleared.")

    def paste_clipboard(self):
        url = self.root.clipboard_get().strip()
        def is_valid_url(url):
            try:
                parsed = urllib.parse.urlparse(url)
                return parsed.scheme in ("http", "https") and bool(parsed.netloc)
            except Exception:
                return False
        if url:
            if not is_valid_url(url):
                self.status_var.set("Clipboard does not contain a valid HTTP or HTTPS URL. Please copy a valid link starting with http:// or https://.")
                return
            if url in self.url_queue:
                self.status_var.set(f"Duplicate link skipped: {url[:60]}")
                return
            self.url_queue.append(url)
            self.queue_listbox.insert(tk.END, url)
            self.status_var.set(f"Added to queue: {url[:60]}")
        else:
            self.status_var.set("Clipboard is empty or not a valid URL.")

    def clear_queue(self):
        self.url_queue.clear()
        self.queue_listbox.delete(0, tk.END)
        self.status_var.set("Queue cleared.")

    def start_processing(self):
        if not self.url_queue:
            messagebox.showwarning("Queue Empty", "Please add at least one URL to the queue.")
            return
        # Disable buttons during processing
        self.convert_button.config(state=tk.DISABLED)
        self.clear_button.config(state=tk.DISABLED)
        self.status_var.set("Starting...")
        thread = threading.Thread(target=process_urls,
                                  args=(self.url_queue.copy(), self.update_status, self.update_progress, self.show_completion_message),
                                  daemon=True)
        thread.start()

    def show_completion_message(self, success, message, errors=None):
        """Shows the final status and enables buttons."""
        final_message = message
        if errors:
            final_message += f"\nEncountered {len(errors)} error(s)."
            # Optionally show detailed errors in a message box or log
            print("\n--- ERRORS ---")
            for err in errors:
                print(err)
            print("--------------")
            # You could uncomment this for a popup, but it might be annoying for many errors
            # messagebox.showerror("Processing Errors", "\n".join(errors))

        self.update_status(final_message)
        if success and not errors:
             messagebox.showinfo("Success", message)
        elif errors :
             messagebox.showwarning("Completed with Errors", final_message)

        # Automatically clear queue after processing
        self.url_queue.clear()
        self.queue_listbox.delete(0, tk.END)

        # Re-enable buttons
        self.convert_button.config(state=tk.NORMAL)
        self.clear_button.config(state=tk.NORMAL)

    def start_processing(self):
        if not self.url_queue:
            messagebox.showwarning("Queue Empty", "Please add at least one URL to the queue.")
            return
        # Disable buttons during processing
        self.convert_button.config(state=tk.DISABLED)
        self.clear_button.config(state=tk.DISABLED)
        self.status_var.set("Starting...")
        thread = threading.Thread(target=process_urls,
                                  args=(self.url_queue.copy(), self.update_status, self.update_progress, self.show_completion_message),
                                  daemon=True)
        thread.start()

# --- Main Execution ---

if __name__ == "__main__":
    # Use ThemedTk for automatic theme application
    root = ThemedTk(theme=THEME_NAME)
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.ico")
    if os.path.exists(icon_path):
        root.iconbitmap(icon_path)
    app = App(root)
    root.mainloop()