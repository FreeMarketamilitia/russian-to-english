# Russian to English PDF/DOC Translator

This Python script extracts text from PDF or DOC files and translates it from Russian to English using the Google Gemini API. It supports multi-page documents (e.g., 20+ pages) by splitting text into manageable chunks.

## Prerequisites

### Software Requirements
- Python 3.7+
- Operating system: Linux, macOS, or Windows (with additional setup for DOC files)

### Python Libraries
Install the required libraries:
pip install google-generativeai textract

### Additional Dependencies
- For DOC files: Install `antiword`:
  - Ubuntu: sudo apt-get install antiword
  - macOS: brew install antiword (with Homebrew)
  - Windows: Use WSL or switch to `.docx` with a different library (e.g., `python-docx`).
- For scanned PDFs: Install Tesseract for OCR:
  - Ubuntu: sudo apt-get install tesseract-ocr
  - macOS: brew install tesseract
  - Then: pip install textract[ocr]

### API Key
1. Obtain a Gemini API key from [Google AI Studio](https://makersuite.google.com/).
2. Set it as an environment variable:
export GOOGLE_API_KEY='your-api-key-here'

## Usage

1. Save the script as `app.py`.
2. Run it with a file path as an argument:
python translate.py path/to/your/file.pdf
   or
python translate.py path/to/your/file.doc

3. The translated text will be saved as `path/to/your/file_translated.txt`.

## Features
- Handles PDF and DOC files.
- Supports large documents (20+ pages) by splitting text into chunks.
- Uses the official Google Gemini API (`gemini-1.5-flash` model).

## Notes
- Chunk Size: Text is split into ~4000-character chunks to stay within API limits.
- API Quotas: Ensure your API key supports multiple requests for large files.
- Scanned PDFs: Requires Tesseract for OCR if the PDF is image-based.
- Output Quality: The prompt is optimized for accurate translations, retaining context where possible.

## Troubleshooting
- "GOOGLE_API_KEY not set": Ensure the environment variable is set.
- Text extraction fails: Verify the file format and dependencies (e.g., `antiword` for DOC).
- Translation errors: Check API key validity and quotas.

## Example
export GOOGLE_API_KEY='abc123'
python app.py documents/report.pdf
Output: `documents/report_translated.txt`

## License
MIT License - feel free to modify and distribute.
