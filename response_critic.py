import argparse
import json
import os
import sys
from api_utils import generate_content, parse_json_response
from config import EVAL_MODEL_NAME, EVAL_TEMPERATURE, OUTPUT_DIR

def evaluate_roadmap(roadmap, original_skills):
    """Evaluate the generated roadmap for quality and provide improvements"""
    
    # Convert to string if it's a dictionary
    roadmap_text = json.dumps(roadmap, indent=2) if isinstance(roadmap, dict) else roadmap
    skills_text = json.dumps(original_skills, indent=2) if isinstance(original_skills, dict) else original_skills
    
    prompt = f"""
    Please evaluate this learning roadmap against the original extracted skills.
    
    Original Skills:
    {skills_text}
    
    Generated Roadmap:
    {roadmap_text}
    
    Please analyze the roadmap on these criteria:
    1. Coverage: Are all important skills from the original list covered?
    2. Relevance: Is the roadmap relevant to the target job role?
    3. Structure: Is the progression logical and well-structured?
    4. Practicality: Are the resources and timeline realistic?
    5. Completeness: Are there any missing critical elements?
    
    Then, provide specific improvements to enhance the roadmap.
    Finally, provide an improved version of the roadmap that addresses these issues.
    
    Format your response as a JSON with these keys:
    - "evaluation": Your assessment on the 5 criteria
    - "suggested_improvements": List of specific improvements
    - "improved_roadmap": The enhanced roadmap
    """
    
    try:
        system_instruction = "You are an expert evaluator of career roadmaps. Your job is to critique and improve learning paths to ensure they're comprehensive and effective."
        
        result = generate_content(
            model_name=EVAL_MODEL_NAME,
            prompt=prompt, 
            system_instruction=system_instruction,
            temperature=EVAL_TEMPERATURE
        )
        
        return parse_json_response(result)
            
    except Exception as e:
        return {"error": str(e)}

def load_input(roadmap_file, skills_file):
    """Load roadmap and original skills from input files"""
    if not os.path.exists(roadmap_file):
        raise FileNotFoundError(f"Roadmap file not found: {roadmap_file}")
    
    if not os.path.exists(skills_file):
        raise FileNotFoundError(f"Skills file not found: {skills_file}")
    
    with open(roadmap_file, 'r', encoding='utf-8') as f:
        roadmap = json.load(f)
    
    with open(skills_file, 'r', encoding='utf-8') as f:
        skills = json.load(f)
    
    return roadmap, skills

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
    parser = argparse.ArgumentParser(description="Evaluate and improve generated roadmap")
    parser.add_argument("--roadmap", "-r", required=True, help="Path to roadmap JSON file")
    parser.add_argument("--skills", "-s", required=True, help="Path to original skills JSON file")
    parser.add_argument("--output", "-o", help="Output file path")
    
    args = parser.parse_args()
    
    try:
        roadmap, skills = load_input(args.roadmap, args.skills)
        evaluation = evaluate_roadmap(roadmap, skills)
        
        output_path = args.output or os.path.join(OUTPUT_DIR, "evaluated_roadmap.json")
        output = save_output(evaluation, output_path)
        print(output)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
