import argparse
import json
import os
import sys
import time
from pathlib import Path
from datetime import datetime
from config import OUTPUT_DIR, MIN_DELAY_BETWEEN_REQUESTS

# Import all the component modules
from job_description_handler import process_job_description
from skill_extractor import extract_skills
from roadmap_generator import generate_roadmap
from response_critic import evaluate_roadmap
from qa_assistant import interactive_mode

def create_session_folder():
    """Create a new session folder with timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_dir = os.path.join(OUTPUT_DIR, f"session_{timestamp}")
    os.makedirs(session_dir, exist_ok=True)
    return session_dir

def run_pipeline(job_description=None, jd_file=None, output_dir=None, interactive=False):
    """Run the complete pipeline from job description to roadmap"""
    
    # Create session folder if output_dir not specified
    if not output_dir:
        output_dir = create_session_folder()
        print(f"Created session folder: {output_dir}")
    
    # Step 1: Process job description
    print("\n[1/4] Processing job description...")
    jd_data = process_job_description(job_description, jd_file)
    jd_path = os.path.join(output_dir, "job_description.json")
    with open(jd_path, 'w', encoding='utf-8') as f:
        json.dump(jd_data, f, indent=2)
    print(f"Job description processed and saved to {jd_path}")
    
    # Step 2: Extract skills - Enforce rate limit
    print("\n[2/4] Extracting skills...")
    skills_data = extract_skills(jd_data["job_description"])
    
    if "error" in skills_data:
        print(f"Warning: Error in skill extraction: {skills_data['error']}")
        print("Continuing with empty skills data...")
        skills_data = {
            "Technical Skills": [],
            "Soft Skills": [],
            "Domain-Specific Skills": [],
            "Certifications": [],
            "Experience Requirements": []
        }
    
    skills_path = os.path.join(output_dir, "extracted_skills.json")
    with open(skills_path, 'w', encoding='utf-8') as f:
        json.dump(skills_data, f, indent=2)
    print(f"Skills extracted and saved to {skills_path}")
    
    # Add delay between API calls
    time.sleep(MIN_DELAY_BETWEEN_REQUESTS)
    
    # Step 3: Generate roadmap
    print("\n[3/4] Generating learning roadmap...")
    roadmap_data = generate_roadmap(skills_data)
    
    if "error" in roadmap_data:
        print(f"Warning: Error in roadmap generation: {roadmap_data['error']}")
        print("Using simplified roadmap...")
        roadmap_data = {
            "Foundation Phase": {
                "skills": ["Basic fundamentals"],
                "resources": ["Online courses"],
                "projects": ["Simple exercises"],
                "estimated_time": "2-4 weeks"
            },
            "Development Phase": {
                "skills": ["Core skills from extracted list"],
                "resources": ["Documentation and tutorials"],
                "projects": ["Practice projects"],
                "estimated_time": "1-2 months"
            }
        }
    
    roadmap_path = os.path.join(output_dir, "roadmap.json")
    with open(roadmap_path, 'w', encoding='utf-8') as f:
        json.dump(roadmap_data, f, indent=2)
    print(f"Roadmap generated and saved to {roadmap_path}")
    
    # Add delay between API calls
    time.sleep(MIN_DELAY_BETWEEN_REQUESTS)
    
    # Step 4: Evaluate and improve the roadmap
    print("\n[4/4] Evaluating and improving the roadmap...")
    try:
        evaluation_data = evaluate_roadmap(roadmap_data, skills_data)
        if "error" in evaluation_data:
            raise Exception(evaluation_data["error"])
    except Exception as e:
        print(f"Warning: Could not evaluate roadmap: {str(e)}")
        print("Skipping evaluation step...")
        evaluation_data = {
            "evaluation": "Could not perform evaluation due to API rate limits.",
            "suggested_improvements": ["Consider reviewing the roadmap manually."],
            "improved_roadmap": roadmap_data
        }
    
    evaluation_path = os.path.join(output_dir, "evaluated_roadmap.json")
    with open(evaluation_path, 'w', encoding='utf-8') as f:
        json.dump(evaluation_data, f, indent=2)
    print(f"Evaluation complete and saved to {evaluation_path}")
    
    # Extract the improved roadmap for output and interactive mode
    improved_roadmap = evaluation_data.get("improved_roadmap", roadmap_data)
    final_roadmap_path = os.path.join(output_dir, "final_roadmap.json")
    with open(final_roadmap_path, 'w', encoding='utf-8') as f:
        json.dump(improved_roadmap, f, indent=2)
    print(f"\nFinal roadmap saved to {final_roadmap_path}")
    
    # Interactive Q&A mode if requested
    if interactive:
        print("\nStarting interactive Q&A mode...")
        print("Note: Due to API rate limits, responses may be delayed or limited.")
        interactive_mode(improved_roadmap, skills_data)
    
    return {
        "output_dir": output_dir,
        "job_description_path": jd_path,
        "skills_path": skills_path,
        "roadmap_path": roadmap_path,
        "evaluation_path": evaluation_path,
        "final_roadmap_path": final_roadmap_path
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Career Roadmap Generator Pipeline")
    parser.add_argument("--input", "-i", help="Input job description text")
    parser.add_argument("--file", "-f", help="Path to job description file")
    parser.add_argument("--output-dir", "-o", help="Output directory for all files")
    parser.add_argument("--interactive", "-q", action="store_true", help="Start interactive Q&A mode after pipeline completion")
    
    args = parser.parse_args()
    
    if not (args.input or args.file):
        print("Error: Please provide either input text or input file")
        sys.exit(1)
    
    try:
        results = run_pipeline(
            job_description=args.input,
            jd_file=args.file,
            output_dir=args.output_dir,
            interactive=args.interactive
        )
        print("\nPipeline completed successfully!")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
