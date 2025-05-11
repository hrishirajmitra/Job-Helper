import PyPDF2
import io
from api_utils import generate_content, parse_json_response
from config import MODEL_NAME, TEMPERATURE

def extract_text_from_pdf(pdf_file):
    """Extract text content from an uploaded PDF file"""
    try:
        # Create a PDF reader object
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file))
        
        # Extract text from all pages
        text = ""
        for page_num in range(len(pdf_reader.pages)):
            text += pdf_reader.pages[page_num].extract_text()
        
        return text.strip()
    except Exception as e:
        raise Exception(f"Error extracting text from PDF: {str(e)}")

def analyze_cv(cv_text, skills, roadmap):
    """Analyze CV against skills and roadmap to provide feedback"""
    
    # Create a formatted skills list for the prompt
    skills_text = ""
    for category, items in skills.items():
        if isinstance(items, list) and items:
            skills_text += f"{category}:\n"
            for item in items:
                skills_text += f"- {item}\n"
            skills_text += "\n"
    
    # Create a simplified roadmap overview
    roadmap_text = "Learning Roadmap Summary:\n"
    for phase, details in roadmap.items():
        if isinstance(details, dict):
            roadmap_text += f"\n{phase}:\n"
            if "skills" in details and details["skills"]:
                roadmap_text += "Skills to focus on:\n"
                for skill in details["skills"]:
                    roadmap_text += f"- {skill}\n"
    
    # Construct the prompt for CV analysis
    prompt = f"""
    Please analyze this CV/resume against the job skills and learning roadmap. The candidate wants to know how their current skills match with the job requirements and what they need to improve.
    
    CV/RESUME TEXT:
    {cv_text}
    
    JOB SKILLS REQUIRED:
    {skills_text}
    
    {roadmap_text}
    
    Please provide a detailed analysis including:
    1. Skills Match: Which skills from the job requirements are present in the CV
    2. Skills Gap: Important skills that are missing or need improvement
    3. Recommendations: Specific actions to improve the CV based on the roadmap
    4. Additional Suggestions: How to better present existing skills or experience
    
    Format your response as a JSON with these keys:
    - "skills_match": List of matched skills with confidence level (high/medium/low)
    - "skills_gap": List of missing critical skills
    - "recommendations": List of specific actions to take
    - "cv_improvement": General suggestions to improve the resume
    """
    
    try:
        system_instruction = "You are an expert resume analyzer and career coach. Your job is to provide honest, constructive feedback to help job seekers improve their resumes."
        
        result = generate_content(
            model_name=MODEL_NAME,
            prompt=prompt,
            system_instruction=system_instruction,
            temperature=TEMPERATURE
        )
        
        return parse_json_response(result)
            
    except Exception as e:
        return {"error": str(e)}
