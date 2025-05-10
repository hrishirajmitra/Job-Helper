import argparse
import json
import os
import sys
from api_utils import generate_content, parse_json_response
from config import MODEL_NAME, TEMPERATURE, OUTPUT_DIR

def generate_roadmap(skills):
    """Generate a learning roadmap based on extracted skills"""
    
    # Convert skills dictionary to formatted text
    skills_text = ""
    for category, items in skills.items():
        if isinstance(items, list):
            skills_text += f"{category}:\n" + "\n".join([f"- {item}" for item in items]) + "\n\n"
        elif isinstance(items, dict):
            skills_text += f"{category}:\n"
            for subcat, subitems in items.items():
                if isinstance(subitems, list):
                    skills_text += f"  {subcat}:\n" + "\n".join([f"  - {item}" for item in subitems]) + "\n"
                else:
                    skills_text += f"  {subcat}: {subitems}\n"
            skills_text += "\n"
    
    prompt = f"""
    Based on these extracted skills:
    
    {skills_text}
    
    Create a comprehensive learning roadmap with these phases:
    
    1. Foundation Phase - Essential fundamentals to learn first
    2. Development Phase - Building practical skills
    3. Specialization Phase - Advanced topics and specializations
    4. Interview Preparation Phase - Getting ready for job interviews
    
    For each phase, include:
    - Specific skills to focus on
    - Recommended resources (courses, books, etc.)
    - Projects or exercises
    - Estimated time to complete
    
    Format the roadmap as a JSON with phases as main keys.
    """
    
    try:
        system_instruction = "You are an expert career mentor who creates personalized learning roadmaps."
        
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
    """Load skills from input file"""
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file not found: {input_file}")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        return json.load(f)

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
    parser = argparse.ArgumentParser(description="Generate learning roadmap from extracted skills")
    parser.add_argument("--file", "-f", required=True, help="Path to skills JSON file")
    parser.add_argument("--output", "-o", help="Output file path")
    
    args = parser.parse_args()
    
    try:
        skills = load_input(args.file)
        roadmap = generate_roadmap(skills)
        
        output_path = args.output or os.path.join(OUTPUT_DIR, "roadmap.json")
        output = save_output(roadmap, output_path)
        print(output)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
