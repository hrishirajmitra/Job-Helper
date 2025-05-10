import argparse
import json
import os
import sys
from pathlib import Path

def clean_job_description(text):
    """Clean and format job description text"""
    # Remove extra whitespace
    text = ' '.join(text.split())
    # Basic normalization
    return text.strip()

def process_job_description(input_text=None, input_file=None):
    """Process job description from text or file"""
    if input_file and os.path.exists(input_file):
        with open(input_file, 'r', encoding='utf-8') as file:
            job_desc = file.read()
    elif input_text:
        job_desc = input_text
    else:
        raise ValueError("Either input_text or input_file must be provided")
    
    cleaned_jd = clean_job_description(job_desc)
    return {
        "job_description": cleaned_jd,
        "word_count": len(cleaned_jd.split()),
        "char_count": len(cleaned_jd)
    }

def save_output(output_data, output_path=None):
    """Save output to file or return as string"""
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2)
        return f"Output saved to {output_path}"
    else:
        return json.dumps(output_data, indent=2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process job descriptions")
    parser.add_argument("--input", "-i", help="Input job description text")
    parser.add_argument("--file", "-f", help="Path to job description file")
    parser.add_argument("--output", "-o", help="Output file path")
    
    args = parser.parse_args()
    
    if not (args.input or args.file):
        print("Error: Please provide either input text or input file")
        sys.exit(1)
    
    try:
        result = process_job_description(args.input, args.file)
        output = save_output(result, args.output)
        print(output)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
