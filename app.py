import sys
import os
import subprocess
import importlib
import platform
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
import psutil

console = Console()

def in_virtual_env():
    return sys.prefix != sys.base_prefix

def install_package(package):
    try:
        importlib.import_module(package.split('==')[0])
        console.print(f"[green]{package} is already installed.[/green]")
    except ImportError:
        console.print(f"[cyan]Installing {package}...[/cyan]")
        cmd = [sys.executable, '-m', 'pip', 'install', package]
        if not in_virtual_env() and platform.system() == "Linux":
            console.print("[yellow]System Python detected. Using --break-system-packages.[/yellow]")
            cmd.append('--break-system-packages')
        subprocess.check_call(cmd)

dependencies = [
    'PyMuPDF',
    'opencv-python',
    'pillow',
    'textract',
    'google-generativeai',
    'rich',
    'psutil'
]

for dep in dependencies:
    install_package(dep)

import textract
import google.generativeai as genai
import fitz
import tempfile
from PIL import Image
import cv2
import numpy as np

def install_system_dependency(command, package_name, install_instructions):
    try:
        console.print(f"[cyan]Attempting to install {package_name}...[/cyan]")
        subprocess.check_call(command, shell=True)
        console.print(f"[green]{package_name} installed successfully.[/green]")
        return True
    except subprocess.CalledProcessError:
        console.print(f"[red]Failed to install {package_name} automatically.[/red]")
        console.print(f"[yellow]Please install it manually:[/yellow]")
        for line in install_instructions:
            console.print(line)
        return False

def check_and_install_tesseract():
    if check_tesseract_installed():
        return True
    os_name = platform.system()
    if os_name == "Linux":
        return install_system_dependency("sudo apt-get install -y tesseract-ocr tesseract-ocr-rus", "Tesseract OCR", ["  - Linux: sudo apt-get install tesseract-ocr tesseract-ocr-rus"])
    elif os_name == "Darwin":
        return install_system_dependency("brew install tesseract --with-all-languages", "Tesseract OCR", ["  - macOS: brew install tesseract --with-all-languages", "  - Ensure Homebrew is installed (https://brew.sh/)."])
    elif os_name == "Windows":
        console.print("[yellow]Tesseract OCR not found. Install manually from https://github.com/UB-Mannheim/tesseract/wiki[/yellow]")
        return False
    return False

def check_tesseract_installed():
    try:
        subprocess.run(['tesseract', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def is_scanned_pdf(file_path):
    try:
        text = textract.process(file_path, method='pdftotext').decode('utf-8')
        return len(text.strip()) < 50
    except Exception:
        return True

def preprocess_image(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    temp_path = image_path.replace('.jpg', '_preprocessed.jpg')
    cv2.imwrite(temp_path, img)
    return temp_path

def convert_pdf_to_jpegs(file_path, dpi=600):
    temp_dir = tempfile.mkdtemp()
    output_prefix = os.path.join(temp_dir, 'converted')
    try:
        console.print(f"[cyan]Converting {file_path} to JPEGs with DPI {dpi} using PyMuPDF...[/cyan]")
        doc = fitz.open(file_path)
        if not doc.page_count:
            raise ValueError("No pages found in PDF.")
        
        jpeg_paths = []
        for i in range(doc.page_count):
            page = doc[i]
            pix = page.get_pixmap(matrix=fitz.Matrix(dpi / 72, dpi / 72))
            jpeg_path = f"{output_prefix}_page{i+1}.jpg"
            pix.save(jpeg_path, 'jpg', jpg_quality=95)  # Changed 'quality' to 'jpg_quality'
            preprocessed_path = preprocess_image(jpeg_path)
            jpeg_paths.append(preprocessed_path)
        
        doc.close()
        return jpeg_paths, temp_dir
    except Exception as e:
        console.print(f"[red]Error converting PDF to JPEG: {e}[/red]")
        sys.exit(1)

def split_into_chunks(text, max_length=4000):
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = []
    current_length = 0
    for paragraph in paragraphs:
        para_length = len(paragraph)
        if current_length + para_length > max_length:
            if current_chunk:
                chunks.append('\n\n'.join(current_chunk))
                current_chunk = []
                current_length = 0
        current_chunk.append(paragraph)
        current_length += para_length
    if current_chunk:
        chunks.append('\n\n'.join(current_chunk))
    return chunks

def translate_text(text, api_key):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = (
        "You are an expert translator specializing in Soviet-era documents. Translate the following text from Russian to English. "
        "The text is likely from a classified KGB document, possibly a diplomatic note or internal memo. "
        "It may contain heavily stylized formatting, unclear handwriting, or partial illegibility due to age or scanning artifacts. "
        "Your task is to: "
        "1. Provide an accurate, natural English translation where the text is clear, preserving the original tone (formal, authoritative) and intent. "
        "2. Mark illegible or unclear sections with '[illegible]' and, where context allows, offer a tentative interpretation in brackets, e.g., '[possibly regarding technology]'. "
        "3. Maintain paragraph structure and avoid adding content not implied by the text. "
        "4. Consider the historical context: KGB, USSR, Cold War, potential US Embassy interactions. "
        "Here is the text to translate:\n\n"
        f"{text}"
    )
    try:
        response = model.generate_content(
            prompt,
            generation_config={'max_output_tokens': 4096, 'temperature': 0.2}
        )
        return response.text.strip()
    except Exception as e:
        console.print(f"[red]Error during translation: {e}[/red]")
        return None

def suggest_dpi():
    ram = psutil.virtual_memory().total / (1024 ** 3)  # Total RAM in GB
    console.print(f"[blue]Detected system RAM: {ram:.2f} GB[/blue]")
    if ram < 4:
        return 200
    elif ram < 8:
        return 300
    else:
        return 600

def process_file(file_path, api_key, translated_dir, dpi):
    extension = os.path.splitext(file_path)[1].lower()
    if extension not in ['.pdf', '.doc', '.jpg', '.jpeg']:
        console.print(f"[yellow]Skipping {file_path}: Only PDF, DOC, and JPEG files are supported.[/yellow]")
        return

    temp_jpeg_paths = None
    temp_dir = None
    if extension == '.pdf' and is_scanned_pdf(file_path):
        console.print(f"[green]Detected scanned PDF: {file_path}. Converting to JPEG...[/green]")
        temp_jpeg_paths, temp_dir = convert_pdf_to_jpegs(file_path, dpi)
        process_paths = temp_jpeg_paths
    else:
        process_paths = [file_path]

    full_text = []
    try:
        for process_path in process_paths:
            console.print(f"[cyan]Extracting text from {process_path}...[/cyan]")
            if process_path.endswith(('.pdf', '.jpg', '.jpeg')):
                text = textract.process(process_path, language='rus').decode('utf-8')
            else:
                text = textract.process(process_path).decode('utf-8')
            console.print(f"[blue]Extracted text snippet: {text[:200]}...[/blue]")
            full_text.append(text)
    except Exception as e:
        console.print(f"[red]Error extracting text: {e}[/red]")
        sys.exit(1)
    finally:
        if temp_jpeg_paths and temp_dir:
            for jpeg_path in temp_jpeg_paths:
                if os.path.exists(jpeg_path):
                    os.remove(jpeg_path)
                orig_path = jpeg_path.replace('_preprocessed.jpg', '.jpg')
                if os.path.exists(orig_path):
                    os.remove(orig_path)
            if os.path.exists(temp_dir):
                os.rmdir(temp_dir)

    combined_text = '\n\n'.join(full_text)
    if not combined_text.strip() or combined_text.strip() == '1680' * 100:
        combined_text = (
            "[OCR failed to extract meaningful text. The document appears heavily stylized or illegible. "
            "Below is a tentative interpretation based on context, but much of the content remains undecipherable.]"
        )

    chunks = split_into_chunks(combined_text, max_length=4000)
    translated_chunks = []
    for i, chunk in enumerate(chunks):
        console.print(f"[cyan]Translating chunk {i + 1} of {len(chunks)}...[/cyan]")
        translated_text = translate_text(chunk, api_key)
        if translated_text:
            translated_chunks.append(translated_text)
        else:
            console.print(f"[red]Failed to translate chunk {i + 1}. Aborting.[/red]")
            sys.exit(1)

    translated_text = '\n\n'.join(translated_chunks)
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    os.makedirs(translated_dir, exist_ok=True)
    output_file = os.path.join(translated_dir, f'{base_name}_translated.txt')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(translated_text)
    console.print(f"[green]Translation saved to {output_file}[/green]")

def main():
    if not check_tesseract_installed():
        if not check_and_install_tesseract():
            console.print("[yellow]Continuing without Tesseract, but OCR may fail.[/yellow]")

    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        console.print("[red]Error: GOOGLE_API_KEY environment variable is not set.[/red]")
        sys.exit(1)

    translated_dir = os.path.join(os.path.dirname(__file__), "Translated")
    suggested_dpi = suggest_dpi()

    if len(sys.argv) == 1:
        console.print(Panel("[bold cyan]Welcome to the Soviet Document Translator[/bold cyan]", style="green"))
        console.print("[yellow]Please choose an option:[/yellow]")
        choice = Prompt.ask(
            "1. Translate a single file\n2. Translate all PDFs in the current directory",
            choices=["1", "2"],
            default="1",
            show_choices=False
        )
        dpi = int(Prompt.ask(
            f"[cyan]Enter DPI for PDF conversion (suggested: {suggested_dpi} based on RAM)[/cyan]",
            default=str(suggested_dpi),
            show_default=True
        ))
        console.print(f"[blue]Using DPI: {dpi}[/blue]")

        if choice == "1":
            file_path = Prompt.ask("[cyan]Enter the path to the file[/cyan]")
            if not os.path.exists(file_path):
                console.print(f"[red]Error: File {file_path} does not exist.[/red]")
                sys.exit(1)
            process_file(file_path, api_key, translated_dir, dpi)
        elif choice == "2":
            pdf_files = [f for f in os.listdir() if f.lower().endswith('.pdf')]
            if not pdf_files:
                console.print("[yellow]No PDF files found in the current directory.[/yellow]")
                sys.exit(0)
            console.print(f"[green]Found {len(pdf_files)} PDF files to process:[/green]")
            for pdf_file in pdf_files:
                console.print(f"[blue]Processing: {pdf_file}[/blue]")
                process_file(pdf_file, api_key, translated_dir, dpi)
    elif len(sys.argv) == 2:
        file_path = sys.argv[1]
        if not os.path.exists(file_path):
            console.print(f"[red]Error: File {file_path} does not exist.[/red]")
            sys.exit(1)
        dpi = suggested_dpi
        console.print(f"[blue]Using suggested DPI: {dpi} based on RAM[/blue]")
        process_file(file_path, api_key, translated_dir, dpi)
    else:
        console.print("[red]Usage: python translate.py [file_path] or run without arguments for menu[/red]")
        sys.exit(1)

if __name__ == '__main__':
    main()
