import os
import re
import pypdf
from typing import  Optional


def extract_text_from_pdf(pdf_path: str) -> str:
    if not os.path.exists(pdf_path):
        print(f"Warning: PDF file not found at {pdf_path}")
        return ""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = pypdf.PdfReader(file)
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


def extract_words_from_text(text: str, keep_spaces: bool = False, preserve_all: bool = False) -> str:
    """
    Extract words from text with minimal processing.
    
    Args:
        text: The input text to process
        keep_spaces: Whether to keep spaces between words
        preserve_all: Whether to preserve all characters (ignored in this implementation)
    
    Returns:
        Processed text as a string
    """
    # Simple split by whitespace
    words = []
    for line in text.splitlines():
        line = line.strip().lower()
        if line:
            words.extend([word for word in line.split() if word])
    
    # Join with or without spaces
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

def extract_cv_information(text: str) -> str:
    extracted_info = {}
    
    job_title_pattern = r'^([A-Z][A-Z\s]+)(?=\n)'
    job_title_match = re.search(job_title_pattern, text, re.MULTILINE)
    if job_title_match:
        extracted_info['Job_Title'] = job_title_match.group(1).strip()
    
    skills_pattern = r'Skills\s*\n+(.*?)(?=\n\s*[A-Z][a-z]+\s*\n|$)'
    skills_match = re.search(skills_pattern, text, re.DOTALL | re.IGNORECASE)
    if skills_match:
        skills_text = skills_match.group(1).strip()
        skills_text = re.sub(r'\n+', ' ', skills_text)
        skills_text = re.sub(r'\s+', ' ', skills_text)
        extracted_info['Skills'] = skills_text
    
    summary_pattern = r'Summary\s*\n+(.*?)(?=\n\s*[A-Z][a-z]+\s*\n|$)'
    summary_match = re.search(summary_pattern, text, re.DOTALL | re.IGNORECASE)
    if summary_match:
        summary_text = summary_match.group(1).strip()
        summary_text = re.sub(r'\n+', ' ', summary_text)
        summary_text = re.sub(r'\s+', ' ', summary_text)
        extracted_info['Summary'] = summary_text
    
    highlights_pattern = r'Highlights\s*\n+(.*?)(?=\n\s*[A-Z][a-z]+\s*\n|$)'
    highlights_match = re.search(highlights_pattern, text, re.DOTALL | re.IGNORECASE)
    if highlights_match:
        highlights_text = highlights_match.group(1).strip()
        highlights_text = re.sub(r'\n+', ' ', highlights_text)
        highlights_text = re.sub(r'\s+', ' ', highlights_text)
        extracted_info['Highlights'] = highlights_text
    
    accomplishments_pattern = r'Accomplishments\s*\n+(.*?)(?=\n\s*[A-Z][a-z]+\s*\n|$)'
    accomplishments_match = re.search(accomplishments_pattern, text, re.DOTALL | re.IGNORECASE)
    if accomplishments_match:
        accomplishments_text = accomplishments_match.group(1).strip()
        accomplishments_text = re.sub(r'\n+', ' ', accomplishments_text)
        accomplishments_text = re.sub(r'\s+', ' ', accomplishments_text)
        extracted_info['Accomplishments'] = accomplishments_text
    
    experience_pattern = r'Experience\s*\n+(.*?)(?=\n\s*Education|$)'
    experience_match = re.search(experience_pattern, text, re.DOTALL | re.IGNORECASE)
    
    companies = []
    dates = []
    positions = []
    
    if experience_match:
        experience_text = experience_match.group(1)
        
        work_entries = re.findall(r'(\d{2}/\d{4}\s*-\s*\d{2}/\d{4})\s*\n([^\n,]+)\s+City\s*,\s*State\s+([^\n]+)', experience_text)
        
        for entry in work_entries:
            dates.append(entry[0].strip())
            companies.append(entry[1].strip())
            positions.append(entry[2].strip())
    
    education_pattern = r'Education\s*\n+(.*?)(?=\n\s*Certifications|\n\s*Interests|\n\s*Additional Information|$)'
    education_match = re.search(education_pattern, text, re.DOTALL | re.IGNORECASE)
    if education_match:
        education_text = education_match.group(1).strip()
        
        school_pattern = r'([A-Za-z\s]+(?:College|University))'
        school_match = re.search(school_pattern, education_text)
        
        degree_pattern = r'(Associate|Bachelor|Master|PhD).*?:\s*([A-Za-z\s]+)'
        degree_match = re.search(degree_pattern, education_text)
        
        year_pattern = r'\b(19|20)\d{2}\b'
        years = re.findall(year_pattern, education_text)
        
        education_clean = education_text
        education_clean = re.sub(r'\n+', ' ', education_clean)
        education_clean = re.sub(r'\s+', ' ', education_clean)
        
        extracted_info['Education'] = {
            'Full_Text': education_clean,
            'School': school_match.group(1).strip() if school_match else None,
            'Degree': f"{degree_match.group(1)} in {degree_match.group(2).strip()}" if degree_match else None,
            'Years': ', '.join(years) if years else None
        }
    
    result = "=" * 52 + "\n"
    result += "                        CV Summary (REGEX) \n"
    result += "=" * 52 + "\n\n"
    
    if 'Job_Title' in extracted_info:
        result += "JOB TITLE:\n"
        result += f"  {extracted_info['Job_Title']}\n\n"
    
    if 'Skills' in extracted_info:
        result += "SKILLS:\n"
        result += f"  {extracted_info['Skills']}\n\n"
    
    if 'Summary' in extracted_info:
        result += "SUMMARY:\n"
        result += f"  {extracted_info['Summary']}\n\n"
    
    if 'Highlights' in extracted_info:
        result += "HIGHLIGHTS:\n"
        result += f"  {extracted_info['Highlights']}\n\n"
    
    if 'Accomplishments' in extracted_info:
        result += "ACCOMPLISHMENTS:\n"
        result += f"  {extracted_info['Accomplishments']}\n\n"
    
    if dates and companies:
        result += "WORK EXPERIENCE:\n"
        for i in range(len(dates)):
            date = dates[i] if i < len(dates) else "N/A"
            company = companies[i] if i < len(companies) else "N/A"
            position = positions[i] if i < len(positions) else "N/A"
            
            result += f"  Date     : {date}\n"
            result += f"  Company  : {company}\n"
            result += f"  Position : {position}\n"
            if i < len(dates) - 1:
                result += f"  {'.' * 50}\n"
        result += "\n"
    
    if 'Education' in extracted_info:
        result += "EDUCATION:\n"
        edu = extracted_info['Education']
        
        if edu['School']:
            result += f"  School   : {edu['School']}\n"
        if edu['Degree']:
            result += f"  Degree   : {edu['Degree']}\n"
        if edu['Years']:
            result += f"  Years    : {edu['Years']}\n"
        
        result += f"  Full Info: {edu['Full_Text']}\n\n"
    
    return result

"""
from utils.pdf_extractor import extract_and_save_for_pattern_matching

text = extract_and_save_for_pattern_matching("path/to/your/pdf.pdf")

text = extract_and_save_for_pattern_matching("path/to/your/pdf.pdf", "output/file/path.txt")
"""