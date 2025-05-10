import argparse
import json
import os
import sys
from pathlib import Path
from api_utils import generate_content, parse_json_response
from config import MODEL_NAME, TEMPERATURE, OUTPUT_DIR

def extract_skills(job_description):
    """Extract skills from job description using LLM"""
    prompt = f"""
    Extract all skills from this job description and categorize them. 
    
    Job Description:
    {job_description}
    
    Please categorize skills into these groups:
    1. Technical Skills
    2. Soft Skills
    3. Domain-Specific Skills
    4. Certifications
    5. Experience Requirements
    
    Format your response as a JSON object with these categories as keys.
    """
    
    try:
        system_instruction = "You are a skilled job analyzer that extracts and categorizes required skills from job descriptions."
        
        result = generate_content(
            model_name=MODEL_NAME,
            prompt=prompt,
            system_instruction=system_instruction,
            temperature=TEMPERATURE
        )
        
        return parse_json_response(result)
            
    except Exception as e:
        return {"error": str(e)}

def load_input(input_file):
    """Load job description from input file"""
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file not found: {input_file}")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data.get("job_description", "")

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
    parser = argparse.ArgumentParser(description="Extract skills from job descriptions")
    parser.add_argument("--input", "-i", help="Input job description text")
    parser.add_argument("--file", "-f", help="Path to job description JSON file")
    parser.add_argument("--output", "-o", help="Output file path")
    
    args = parser.parse_args()
    
    try:
        if args.file:
            job_desc = load_input(args.file)
        elif args.input:
            job_desc = args.input
        else:
            print("Error: Please provide either input text or input file")
            sys.exit(1)
        
        skills = extract_skills(job_desc)
        
        output_path = args.output or os.path.join(OUTPUT_DIR, "extracted_skills.json")
        output = save_output(skills, output_path)
        print(output)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
