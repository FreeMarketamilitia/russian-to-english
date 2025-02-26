# Russian-to-English PDF Translator

This Python script translates Russian text from PDF, DOC, JPEG, or JPG files into English using OCR (Tesseract) and the Google Gemini API. It’s designed for Soviet-era documents, handling stylized or illegible text with tentative interpretations. Features include high-DPI PDF-to-JPEG conversion, a rich-text interactive menu, and automatic dependency installation.

## Prerequisites

- Python 3.8+: Ensure Python is installed (python3 --version).
- Operating System: Tested on Linux (Ubuntu), macOS, and Windows (some manual steps may vary).
- Internet: Required for installing dependencies and using the Gemini API.
- Google API Key: Needed for translation (see Step 3).

## Step-by-Step Instructions

### Step 1: Clone or Set Up the Project
1. Navigate to your project directory:
   cd ~/Projects/russian-to-english
2. If using Git (optional):
   - Clone the repository or place app.py in this directory.
   - Example:
     git clone <repository-url>
     cd russian-to-english

### Step 2: Set Up a Virtual Environment
1. Create a virtual environment:
   python3 -m venv venv
2. Activate the virtual environment:
   - Linux/macOS:
     source venv/bin/activate
   - Windows:
     venv\Scripts\activate
3. Verify: You should see (venv) in your terminal prompt.

### Step 3: Configure the Google API Key
1. Obtain a Google API Key:
   - Go to [https://aistudio.google.com/apikey](https://aistudio.google.com/apikey).
   - Create a project, enable the Gemini API, and generate an API key.
2. Set the environment variable:
   - Linux/macOS:
     export GOOGLE_API_KEY='your-api-key-here'
   - Windows:
     set GOOGLE_API_KEY=your-api-key-here
   - Alternatively, add it to your shell profile (e.g., ~/.bashrc) for persistence:
     echo "export GOOGLE_API_KEY='your-api-key-here'" >> ~/.bashrc
     source ~/.bashrc

### Step 4: Install System Dependencies
The script attempts to install Tesseract automatically, but it may require manual intervention due to permissions.

1. Tesseract OCR:
   - Linux (Ubuntu):
     sudo apt-get update
     sudo apt-get install -y tesseract-ocr tesseract-ocr-rus
   - macOS (with Homebrew):
     brew install tesseract --with-all-languages
     (Install Homebrew first if needed: /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)")
   - Windows:
     - Download and install from https://github.com/UB-Mannheim/tesseract/wiki.
     - Add Tesseract to your system PATH (e.g., C:\Program Files\Tesseract-OCR).

2. Verify Tesseract:
   tesseract --version
   If this fails, ensure the installation completed and the binary is in your PATH.

### Step 5: Run the Script
1. Ensure you’re in the virtual environment:
   source venv/bin/activate  # Linux/macOS
   # or
   venv\Scripts\activate     # Windows
2. Run with interactive menu:
   python3 app.py

   | Display Item                  | Details                                                                 |
   |-------------------------------|-------------------------------------------------------------------------|
   | RAM Detection                 | Detected system RAM: X.XX GB                                            |
   | Welcome Message               | ╭─────────────── Welcome to the Soviet Document Translator ───────────────╮ |
   |                               | │                                                                         │ |
   |                               | ╰─────────────────────────────────────────────────────────────────────────╯ |
   | Prompt                        | [yellow]Please choose an option:[/yellow]                               |

   | Action                        | Description                                                             |
   |-------------------------------|-------------------------------------------------------------------------|
   | Option 1: Translate a single file | Enter a file path (e.g., my_doc.pdf) to process a specific file.       |
   | Option 2: Translate all PDFs  | Process all PDFs in the current directory automatically.                |
   | DPI Prompt                    | Enter a DPI value (suggested based on RAM: 200 for <4 GB, 300 for 4-8 GB, 600 for >8 GB). |

3. Run with a specific file:
   python3 app.py path/to/your_file.pdf
   - Uses the RAM-suggested DPI automatically.

### Step 6: Review Output
- Translated files are saved in a Translated subdirectory (e.g., Translated/your_file_translated.txt).
- Check console output for progress (e.g., OCR snippets, errors).

## Troubleshooting

- “GOOGLE_API_KEY not set”:
  - Ensure you set the environment variable (Step 3).
- “Tesseract not found”:
  - Install manually (Step 4) and verify with tesseract --version.
- Slow Conversion:
  - Lower the DPI when prompted (e.g., 300 instead of 600) if RAM is limited.
- OCR Fails (e.g., “1680” repeated):
  - Check the PDF for legibility; adjust DPI or preprocessing in preprocess_image if needed.

## Features
- File Support: PDF, DOC, JPEG, JPG.
- High-DPI Conversion: Uses PyMuPDF for fast, high-quality PDF-to-JPEG conversion (up to 600 DPI).
- OCR: Tesseract with Russian language support.
- Translation: Google Gemini API with context-aware prompts for Soviet documents.
- Interactive Menu: Rich-text interface with DPI selection.
- RAM Detection: Suggests DPI based on system memory.

## Dependencies
- Python Libraries: Installed automatically (PyMuPDF, opencv-python, pillow, textract, google-generativeai, rich, psutil).
- System: Tesseract OCR (manual install may be required).

## Notes
- Performance: High DPI (e.g., 600) requires more RAM and time but improves OCR accuracy. Adjust based on your system.
- Security: Keep your Google API key private; avoid committing it to version control.

For issues or enhancements, feel free to modify app.py or raise a request!
