# WebP URL to PNG Converter

A desktop application for batch downloading and converting images from web URLs (including WebP) to PNG format, with a modern Deep Blue Ocean themed GUI. Built with Python and PyQt5/Tkinter.

## Features

- **Queue-based Link Management**: Add multiple image URLs to a queue for batch processing.
- **Clipboard Integration**: Paste URLs directly from your clipboard with validation.
- **Deep Blue Ocean Theme**: Visually appealing, modern dark UI for comfortable use.
- **Robust Error Handling**: Graceful handling of invalid URLs, network errors, and unsupported image formats.
- **Automatic Filename Generation**: Smart naming for downloaded images, avoiding overwrites.
- **Progress and Status Updates**: Real-time feedback on download and conversion progress.
- **Clear Queue and Fields**: Easily clear the queue or status fields with dedicated buttons.
- **Credits Display**: Author credits shown in the GUI.

## Setup Instructions

1. **Clone or Download** this repository to your local machine.
2. **Install Dependencies**:
   ```
   pip install -r requirements.txt
   ```
3. **Run the Application**:
   ```
   python main.py
   ```

## Usage Guide

1. **Paste a Link**: Copy an image URL (must start with http:// or https://), then click the "Paste" button to add it to the queue.
2. **Queue Management**: Add as many links as you want. Use "Clear Queue" to remove all links.
3. **Convert & Save**: Click "Convert & Save PNGs" to start downloading and converting all queued links. Images are saved to your Downloads folder.
4. **Status Updates**: Watch the status label for progress and error messages.
5. **Clear Fields**: Use the "Clear" button to reset the status field.

## Detailed Feature List

- **Queue-based Link Management**: Prevents duplicate links, allows batch processing.
- **Clipboard Validation**: Only accepts valid HTTP/HTTPS URLs; warns if invalid or duplicate.
- **Error Handling**: Handles network errors, invalid images, and file conflicts with clear messages.
- **Theme**: Custom deep blue ocean color palette for all UI elements.
- **Output Location**: Images are saved in the user's Downloads folder with unique, sanitized filenames.
- **Dependencies**: Uses PyQt5/Tkinter for GUI, requests for downloading, Pillow for image conversion, and other libraries for extended compatibility.

## Dependencies

- PyQt5
- requests
- beautifulsoup4
- Pillow
- requests-html
- selenium
- undetected-chromedriver
- distutils

Install all dependencies with:
```
pip install -r requirements.txt
```

## Build Instructions (Optional)

To build a standalone executable (Windows):
1. Ensure `pyinstaller` is installed:
   ```
   pip install pyinstaller
   ```
2. Run:
   ```
   pyinstaller main.spec
   ```
3. The executable will be in the `dist/` folder.

## Credits

by @DangerousPixel

---
For any issues or feature requests, please open an issue on the repository.