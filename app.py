import sys
import os
import textract
import google.generativeai as genai

def split_into_chunks(text, max_length=4000):
    """Split text into chunks of max_length characters, preserving paragraphs."""
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
    """Translate text from Russian to English using Gemini API."""
    # Configure the API
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')  # Adjust model as needed

    # Improved prompt for better output
    prompt = (
        "Translate the following text from Russian to English. "
        "Ensure the translation is accurate, preserves the original meaning and context, "
        "and uses natural, idiomatic English. Maintain paragraph structure and avoid altering the content:\n\n"
        f"{text}"
    )

    try:
        # Generate translation
        response = model.generate_content(
            prompt,
            generation_config={
                'max_output_tokens': 4096,  # Adjust based on model limits
                'temperature': 0.0  # Deterministic output
            }
        )
        return response.text.strip()
    except Exception as e:
        print(f'Error during translation: {e}')
        return None

def main():
    # Check if file path is provided
    if len(sys.argv) != 2:
        print('Usage: python translate.py <file_path>')
        sys.exit(1)

    file_path = sys.argv[1]

    # Verify file exists
    if not os.path.exists(file_path):
        print(f'Error: File {file_path} does not exist.')
        sys.exit(1)

    # Check file extension
    extension = os.path.splitext(file_path)[1].lower()
    if extension not in ['.pdf', '.doc']:
        print('Error: Only PDF and DOC files are supported.')
        sys.exit(1)

    # Extract text from the file
    try:
        text = textract.process(file_path).decode('utf-8')
    except Exception as e:
        print(f'Error extracting text: {e}')
        sys.exit(1)

    # Get API key from environment variable
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print('Error: GOOGLE_API_KEY environment variable is not set.')
        sys.exit(1)

    # Split text into chunks
    chunks = split_into_chunks(text, max_length=4000)

    # Translate each chunk
    translated_chunks = []
    for i, chunk in enumerate(chunks):
        print(f'Translating chunk {i + 1} of {len(chunks)}...')
        translated_text = translate_text(chunk, api_key)
        if translated_text:
            translated_chunks.append(translated_text)
        else:
            print(f'Failed to translate chunk {i + 1}. Aborting.')
            sys.exit(1)

    # Combine translated chunks
    translated_text = '\n\n'.join(translated_chunks)

    # Save to output file
    base_name = os.path.splitext(file_path)[0]
    output_file = f'{base_name}_translated.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(translated_text)

    print(f'Translation saved to {output_file}')

if __name__ == '__main__':
    main()
