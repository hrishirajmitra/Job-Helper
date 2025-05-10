import argparse
import json
import os
import sys
from api_utils import generate_content
from config import MODEL_NAME, TEMPERATURE

def answer_question(question, roadmap, skills=None):
    """Answer questions about the roadmap and skills"""
    
    # Convert to string if they're dictionaries
    roadmap_text = json.dumps(roadmap, indent=2) if isinstance(roadmap, dict) else roadmap
    skills_text = ""
    if skills:
        skills_text = f"\nExtracted Skills:\n{json.dumps(skills, indent=2)}" if isinstance(skills, dict) else f"\nExtracted Skills:\n{skills}"
    
    prompt = f"""
    Based on this learning roadmap:{skills_text}
    
    Roadmap:
    {roadmap_text}
    
    Please answer this question:
    {question}
    
    Provide a clear, helpful response that addresses the question directly.
    """
    
    try:
        system_instruction = "You are a helpful career guidance assistant that provides advice based on learning roadmaps and skill requirements."
        
        result = generate_content(
            model_name=MODEL_NAME,
            prompt=prompt,
            system_instruction=system_instruction,
            temperature=TEMPERATURE
        )
        
        return {
            "question": question,
            "answer": result
        }
            
    except Exception as e:
        return {"error": str(e)}

def load_input(roadmap_file, skills_file=None):
    """Load roadmap and optional skills from input files"""
    if not os.path.exists(roadmap_file):
        raise FileNotFoundError(f"Roadmap file not found: {roadmap_file}")
    
    with open(roadmap_file, 'r', encoding='utf-8') as f:
        roadmap = json.load(f)
    
    skills = None
    if skills_file and os.path.exists(skills_file):
        with open(skills_file, 'r', encoding='utf-8') as f:
            skills = json.load(f)
    
    return roadmap, skills

def interactive_mode(roadmap, skills=None):
    """Interactive Q&A session"""
    print("Welcome to the Career Roadmap Q&A Assistant!")
    print("Ask questions about your roadmap or type 'exit' to quit.")
    print()
    
    while True:
        question = input("Your question: ")
        if question.lower() in ['exit', 'quit', 'q']:
            print("Goodbye!")
            break
            
        if not question.strip():
            continue
            
        response = answer_question(question, roadmap, skills)
        if "error" in response:
            print(f"Error: {response['error']}")
        else:
            print("\nAnswer:")
            print(response["answer"])
            print()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Q&A Assistant for learning roadmap")
    parser.add_argument("--roadmap", "-r", required=True, help="Path to roadmap JSON file")
    parser.add_argument("--skills", "-s", help="Path to skills JSON file (optional)")
    parser.add_argument("--question", "-q", help="Single question to answer (optional)")
    parser.add_argument("--output", "-o", help="Output file path (for single question mode)")
    
    args = parser.parse_args()
    
    try:
        roadmap, skills = load_input(args.roadmap, args.skills)
        
        if args.question:
            # Single question mode
            response = answer_question(args.question, roadmap, skills)
            
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(response, f, indent=2)
                print(f"Answer saved to {args.output}")
            else:
                print(json.dumps(response, indent=2))
        else:
            # Interactive mode
            interactive_mode(roadmap, skills)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
