import os
import re
import PyPDF2
from typing import  Optional


def extract_text_from_pdf(pdf_path: str) -> str:
    if not os.path.exists(pdf_path):
        print(f"Warning: PDF file not found at {pdf_path}")
        return ""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            
            # Extract text from each page
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + " "
                    
            return text
    except Exception as e:
        print(f"Error extracting text from PDF {pdf_path}: {e}")
        return ""


def extract_words_from_text(text: str, keep_spaces: bool = False) -> str:
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip().lower()
    
    words = [word for word in text.split() if word]
    
    if keep_spaces:
        return " ".join(words)
    else:
        return "".join(words)

def extract_words_from_pdf(pdf_path: str, keep_spaces: bool = False) -> str:
    raw_text = extract_text_from_pdf(pdf_path)
    return extract_words_from_text(raw_text, keep_spaces)


def save_text_to_file(text: str, output_path: str) -> None:
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(text)
    except Exception as e:
        print(f"Error saving text to {output_path}: {e}")


def extract_and_save_for_pattern_matching(pdf_path: str, output_path: Optional[str] = None) -> str:
    words = extract_words_from_pdf(pdf_path, keep_spaces=True)
    
    if output_path:
        # For pattern matching, save as a single string with spaces between words
        save_text_to_file(words, output_path)
    
    return words

def extract_and_save_for_regex(pdf_path: str, output_path: Optional[str] = None) -> str:
    text = extract_text_from_pdf(pdf_path)
    
    if output_path:
        save_text_to_file(text, output_path)
    
    return text

"""
from utils.pdf_extractor import extract_and_save_for_pattern_matching

text = extract_and_save_for_pattern_matching("path/to/your/pdf.pdf")

text = extract_and_save_for_pattern_matching("path/to/your/pdf.pdf", "output/file/path.txt")
"""