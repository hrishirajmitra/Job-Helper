import streamlit as st
import json
import time
import os
import sys
import pandas as pd
from datetime import datetime
from pathlib import Path

# Add the current directory to sys.path to ensure imports work
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Import the necessary components
try:
    from job_description_handler import process_job_description
    from skill_extractor import extract_skills
    from roadmap_generator import generate_roadmap
    from response_critic import evaluate_roadmap
    from qa_assistant import answer_question
    from config import OUTPUT_DIR, MIN_DELAY_BETWEEN_REQUESTS
    
    # Check if API key is configured
    from config import GEMINI_API_KEY
    if not GEMINI_API_KEY:
        st.error("⚠️ Gemini API Key is not configured! Please check your .env file.")
        st.stop()
except ImportError as e:
    st.error(f"Failed to import required modules: {str(e)}")
    st.write("Make sure all dependencies are installed:")
    st.code("pip install -r requirements.txt")
    st.stop()
except Exception as e:
    st.error(f"Error during startup: {str(e)}")
    st.stop()

# Import the CV analyzer functions
from cv_analyzer import extract_text_from_pdf, analyze_cv

# Set page configuration
st.set_page_config(
    page_title="Career Roadmap Generator",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .skill-category {
        margin-top: 10px;
        padding: 10px;
        border-radius: 5px;
        background-color: rgba(0,0,0,0.05);
    }
    .skill-item {
        margin-bottom: 5px;
        padding-left: 10px;
        border-left: 3px solid;
    }
    .tech-skill { border-left-color: #2196F3; }
    .soft-skill { border-left-color: #4CAF50; }
    .domain-skill { border-left-color: #FF9800; }
    .cert-skill { border-left-color: #9C27B0; }
    .exp-skill { border-left-color: #F44336; }
    .other-skill { border-left-color: #607D8B; }
    
    .phase-container {
        margin-top: 15px;
        padding: 15px;
        border-radius: 5px;
        background-color: rgba(0,0,0,0.03);
    }
    .phase-header {
        font-size: 1.3rem;
        font-weight: bold;
        margin-bottom: 10px;
        padding-bottom: 5px;
        border-bottom: 2px solid;
    }
    .foundation-phase { border-color: #2196F3; }
    .development-phase { border-color: #4CAF50; }
    .specialization-phase { border-color: #9C27B0; }
    .interview-phase { border-color: #F44336; }
    .other-phase { border-color: #FF9800; }
    
    .section-title {
        font-size: 1.1rem;
        font-weight: bold;
        margin-top: 10px;
        margin-bottom: 5px;
    }
    
    .time-estimate {
        display: inline-block;
        padding: 5px 10px;
        background-color: rgba(33, 150, 243, 0.1);
        border-radius: 15px;
        font-weight: bold;
    }
    
    .improvement-item {
        background-color: rgba(255, 193, 7, 0.1);
        padding: 10px;
        margin-bottom: 8px;
        border-left: 3px solid #FFC107;
    }
    
    .evaluation-metric {
        margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Create outputs directory if it doesn't exist
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def create_session_folder():
    """Create a new session folder with timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_dir = os.path.join(OUTPUT_DIR, f"session_{timestamp}")
    os.makedirs(session_dir, exist_ok=True)
    return session_dir

def process_job_description_streamlit(job_description):
    """Process job description and return the pipeline results"""
    
    # Create a progress bar for the pipeline
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Create a session folder
    output_dir = create_session_folder()
    
    # Step 1: Process job description
    status_text.text("Processing job description...")
    jd_data = process_job_description(job_description, None)
    jd_path = os.path.join(output_dir, "job_description.json")
    with open(jd_path, 'w', encoding='utf-8') as f:
        json.dump(jd_data, f, indent=2)
    progress_bar.progress(25)
    
    # Step 2: Extract skills
    status_text.text("Extracting skills from job description...")
    skills_data = extract_skills(jd_data["job_description"])
    
    if "error" in skills_data:
        st.warning(f"Warning: Error in skill extraction: {skills_data['error']}")
        st.info("Continuing with empty skills data...")
        skills_data = {
            "Technical Skills": [],
            "Soft Skills": [],
            "Domain-Specific Skills": [],
            "Certifications": [],
            "Experience Requirements": []
        }
    elif "raw_response" in skills_data:
        # Try to parse JSON from raw_response if it looks like JSON
        try:
            raw_text = skills_data["raw_response"]
            if isinstance(raw_text, str) and "{" in raw_text and "}" in raw_text:
                # Extract JSON part if embedded in text
                json_start = raw_text.find("{")
                json_end = raw_text.rfind("}") + 1
                if json_start >= 0 and json_end > json_start:
                    json_text = raw_text[json_start:json_end]
                    parsed_data = json.loads(json_text)
                    if isinstance(parsed_data, dict) and any(key in parsed_data for key in ["Technical Skills", "Soft Skills"]):
                        skills_data = parsed_data
        except:
            pass
    
    skills_path = os.path.join(output_dir, "extracted_skills.json")
    with open(skills_path, 'w', encoding='utf-8') as f:
        json.dump(skills_data, f, indent=2)
    progress_bar.progress(50)
    
    # Add delay between API calls
    time.sleep(MIN_DELAY_BETWEEN_REQUESTS)
    
    # Step 3: Generate roadmap
    status_text.text("Generating learning roadmap...")
    roadmap_data = generate_roadmap(skills_data)
    
    if "error" in roadmap_data:
        st.warning(f"Warning: Error in roadmap generation: {roadmap_data['error']}")
        st.info("Using simplified roadmap...")
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
    elif "raw_response" in roadmap_data:
        # Try to parse JSON from raw_response if it looks like JSON
        try:
            raw_text = roadmap_data["raw_response"]
            if isinstance(raw_text, str) and "{" in raw_text and "}" in raw_text:
                # Extract JSON part if embedded in text
                json_start = raw_text.find("{")
                json_end = raw_text.rfind("}") + 1
                if json_start >= 0 and json_end > json_start:
                    json_text = raw_text[json_start:json_end]
                    parsed_data = json.loads(json_text)
                    if isinstance(parsed_data, dict):
                        roadmap_data = parsed_data
        except Exception as e:
            st.warning(f"Could not parse roadmap JSON: {str(e)}")
    
    roadmap_path = os.path.join(output_dir, "roadmap.json")
    with open(roadmap_path, 'w', encoding='utf-8') as f:
        json.dump(roadmap_data, f, indent=2)
    progress_bar.progress(75)
    
    # Add delay between API calls
    time.sleep(MIN_DELAY_BETWEEN_REQUESTS)
    
    # Step 4: Evaluate and improve the roadmap
    status_text.text("Evaluating and improving the roadmap...")
    try:
        evaluation_data = evaluate_roadmap(roadmap_data, skills_data)
        if "error" in evaluation_data:
            raise Exception(evaluation_data["error"])
    except Exception as e:
        st.warning(f"Warning: Could not evaluate roadmap: {str(e)}")
        st.info("Skipping evaluation step...")
        evaluation_data = {
            "evaluation": "Could not perform evaluation due to API rate limits.",
            "suggested_improvements": ["Consider reviewing the roadmap manually."],
            "improved_roadmap": roadmap_data
        }
    
    evaluation_path = os.path.join(output_dir, "evaluated_roadmap.json")
    with open(evaluation_path, 'w', encoding='utf-8') as f:
        json.dump(evaluation_data, f, indent=2)
    
    # Extract the improved roadmap
    improved_roadmap = evaluation_data.get("improved_roadmap", roadmap_data)
    if isinstance(improved_roadmap, str):
        # Try to parse if it's a JSON string
        try:
            improved_roadmap = json.loads(improved_roadmap)
        except:
            pass
            
    final_roadmap_path = os.path.join(output_dir, "final_roadmap.json")
    with open(final_roadmap_path, 'w', encoding='utf-8') as f:
        json.dump(improved_roadmap, f, indent=2)
    
    progress_bar.progress(100)
    status_text.text("Processing complete!")
    
    return {
        "jd_data": jd_data,
        "skills_data": skills_data,
        "roadmap_data": roadmap_data,
        "evaluation_data": evaluation_data,
        "improved_roadmap": improved_roadmap,
        "output_dir": output_dir
    }

def display_skills(skills):
    """Display extracted skills in a readable format with visual styling"""
    if "raw_response" in skills:
        # Try to parse the raw_response if it appears to be JSON
        raw_text = skills["raw_response"]
        try:
            if isinstance(raw_text, str) and (raw_text.strip().startswith("{") or raw_text.strip().startswith("[")):
                parsed_skills = json.loads(raw_text)
                # If successful, display the parsed skills instead
                if isinstance(parsed_skills, dict):
                    st.success("Successfully parsed skills from raw response")
                    return display_skills(parsed_skills)
        except:
            pass
            
        # If parsing fails, show the raw text
        st.warning("Skills are in raw text format, attempting to display as-is:")
        st.text(raw_text)
        return
    
    # Check if we have any skills to display
    has_skills = False
    for category, items in skills.items():
        if isinstance(items, list) and items:
            has_skills = True
            break
        elif isinstance(items, dict) and items:
            has_skills = True
            break
    
    if not has_skills:
        st.info("No skills were extracted. Try a more detailed job description.")
        return
    
    # Display skills by category with better formatting
    for category, items in skills.items():
        if not items:  # Skip empty categories
            continue
            
        # Determine category styling
        if "technical" in category.lower():
            emoji = "💻"
            css_class = "tech-skill"
        elif "soft" in category.lower():
            emoji = "🤝"
            css_class = "soft-skill"
        elif "domain" in category.lower():
            emoji = "🔍"
            css_class = "domain-skill"
        elif "certif" in category.lower():
            emoji = "🏆"
            css_class = "cert-skill"
        elif "experience" in category.lower():
            emoji = "⏱️"
            css_class = "exp-skill"
        else:
            emoji = "✅"
            css_class = "other-skill"
        
        # Create expandable section for this category
        with st.expander(f"{emoji} {category} ({len(items) if isinstance(items, list) else 'multiple'})", expanded=True):
            if isinstance(items, list):
                # Create styled list of skills
                for skill in items:
                    st.markdown(f"""<div class="skill-item {css_class}">{skill}</div>""", unsafe_allow_html=True)
            elif isinstance(items, dict):
                # Handle nested structure
                for subcat, subitems in items.items():
                    st.markdown(f"**{subcat}**")
                    if isinstance(subitems, list) and subitems:
                        for item in subitems:
                            st.markdown(f"""<div class="skill-item {css_class}">{item}</div>""", unsafe_allow_html=True)
                    elif subitems:
                        st.markdown(f"""<div class="skill-item {css_class}">{subitems}</div>""", unsafe_allow_html=True)

def display_roadmap_phase(phase_name, phase_data):
    """Display a single roadmap phase with better formatting"""
    # Determine phase-specific styling
    if "foundation" in phase_name.lower():
        emoji = "🏗️"
        phase_class = "foundation-phase"
    elif "development" in phase_name.lower():
        emoji = "🛠️"
        phase_class = "development-phase"
    elif "specialization" in phase_name.lower():
        emoji = "🔍"
        phase_class = "specialization-phase"
    elif "interview" in phase_name.lower():
        emoji = "🎯"
        phase_class = "interview-phase"
    else:
        emoji = "📝"
        phase_class = "other-phase"
    
    # Create container with a header for this phase
    st.markdown(f"""
    <div style="padding: 15px; margin-bottom: 20px; border-radius: 5px; border-left: 5px solid #4CAF50; background-color: #f8f9fa;">
        <h3 style="color: #2E7D32;">{emoji} {phase_name}</h3>
    """, unsafe_allow_html=True)
    
    # Skills to focus on
    if "skills" in phase_data and phase_data["skills"]:
        st.markdown('<h4 style="color: #1976D2;">Skills to Focus On:</h4>', unsafe_allow_html=True)
        skills_list = ""
        for skill in phase_data["skills"]:
            skills_list += f"- {skill}\n"
        st.markdown(skills_list)
    
    # Recommended resources with improved formatting for complex objects
    if "resources" in phase_data and phase_data["resources"]:
        st.markdown('<h4 style="color: #1976D2;">Recommended Resources:</h4>', unsafe_allow_html=True)
        
        for resource in phase_data["resources"]:
            # Handle different resource formats
            if isinstance(resource, dict):
                # Format complex resource object
                if "name" in resource:
                    resource_html = f"<div style='margin-bottom: 8px; padding: 8px; background-color: rgba(0,0,0,0.03); border-radius: 4px;'>"
                    
                    # Resource name with appropriate styling
                    resource_html += f"<strong>{resource['name']}</strong>"
                    
                    # Handle type if present
                    if "type" in resource:
                        resource_html += f" <span style='background-color: #e3f2fd; padding: 2px 6px; border-radius: 4px; font-size: 0.8em;'>{resource['type']}</span>"
                    
                    # Handle author if present
                    if "author" in resource and resource["author"]:
                        resource_html += f"<br><em>by {resource['author']}</em>"
                    
                    # Handle link if present
                    if "link" in resource and resource["link"]:
                        resource_html += f"<br><a href='{resource['link']}' target='_blank'>Visit Resource</a>"
                    
                    resource_html += "</div>"
                    st.markdown(resource_html, unsafe_allow_html=True)
                else:
                    # Fallback for dictionaries without expected structure
                    st.write(f"- {resource}")
            else:
                # Simple string resources
                st.write(f"- {resource}")
    
    # Projects or exercises
    if "projects" in phase_data and phase_data["projects"]:
        st.markdown('<h4 style="color: #1976D2;">Projects & Exercises:</h4>', unsafe_allow_html=True)
        projects_list = ""
        for project in phase_data["projects"]:
            if isinstance(project, dict) and "name" in project:
                # Format complex project object
                project_desc = project["name"]
                if "description" in project:
                    project_desc += f": {project['description']}"
                projects_list += f"- {project_desc}\n"
            else:
                projects_list += f"- {project}\n"
        st.markdown(projects_list)
    
    # Estimated time
    if "estimated_time" in phase_data:
        st.markdown('<h4 style="color: #1976D2;">Estimated Time:</h4>', unsafe_allow_html=True)
        st.markdown(f"""
        <div style="display: inline-block; padding: 5px 10px; background-color: rgba(33, 150, 243, 0.1); 
                    border-radius: 15px; font-weight: bold;">
            ⏱️ {phase_data["estimated_time"]}
        </div>
        """, unsafe_allow_html=True)
    
    # Close the container
    st.markdown("</div>", unsafe_allow_html=True)

def display_roadmap(roadmap):
    """Display the learning roadmap in a readable format"""
    if "raw_response" in roadmap:
        # Try to parse JSON from raw response
        try:
            raw_text = roadmap["raw_response"]
            if isinstance(raw_text, str) and "{" in raw_text:
                start_idx = raw_text.find("{")
                end_idx = raw_text.rfind("}") + 1
                if start_idx >= 0 and end_idx > start_idx:
                    json_str = raw_text[start_idx:end_idx]
                    parsed_roadmap = json.loads(json_str)
                    if isinstance(parsed_roadmap, dict) and len(parsed_roadmap) > 0:
                        st.success("Successfully parsed roadmap data")
                        return display_roadmap(parsed_roadmap)
        except json.JSONDecodeError:
            pass
        
        # If we can't parse JSON, show the raw text
        st.warning("Roadmap data is in raw format. Displaying as is:")
        st.code(roadmap["raw_response"], language="json")
        return
    
    # Check if roadmap is empty or not properly formatted
    if not isinstance(roadmap, dict) or not roadmap:
        st.warning("No roadmap data available or invalid format.")
        return

    # Define the phase order for consistent display
    phase_order = [
        "Foundation Phase", 
        "Development Phase", 
        "Specialization Phase", 
        "Interview Preparation Phase"
    ]
    
    # Find which phases exist in the roadmap, preserving order
    ordered_phases = []
    
    # First add phases that match our predefined order
    for phase_pattern in phase_order:
        for key in roadmap.keys():
            if phase_pattern.lower() in key.lower():
                ordered_phases.append(key)
                break
    
    # Then add any remaining phases
    for key in roadmap.keys():
        if key not in ordered_phases:
            ordered_phases.append(key)
    
    # Display each phase in the determined order
    for phase in ordered_phases:
        if phase in roadmap:
            phase_data = roadmap[phase]
            if isinstance(phase_data, dict):
                display_roadmap_phase(phase, phase_data)
            elif isinstance(phase_data, str):
                # Try to parse if it's a stringified JSON object
                try:
                    parsed_data = json.loads(phase_data)
                    if isinstance(parsed_data, dict):
                        display_roadmap_phase(phase, parsed_data)
                    else:
                        st.markdown(f"**{phase}**: {phase_data}")
                except:
                    st.markdown(f"**{phase}**: {phase_data}")
            else:
                st.markdown(f"**{phase}**: {str(phase_data)}")

def display_evaluation(evaluation):
    """Display the roadmap evaluation results with better formatting"""
    if "raw_response" in evaluation:
        # Try to parse JSON from raw response
        try:
            raw_text = evaluation["raw_response"]
            if isinstance(raw_text, str) and "{" in raw_text:
                start_idx = raw_text.find("{")
                end_idx = raw_text.rfind("}") + 1
                if start_idx >= 0 and end_idx > start_idx:
                    json_str = raw_text[start_idx:end_idx]
                    parsed_eval = json.loads(json_str)
                    if isinstance(parsed_eval, dict) and len(parsed_eval) > 0:
                        st.success("Successfully parsed evaluation data")
                        return display_evaluation(parsed_eval)
        except json.JSONDecodeError:
            pass
            
        st.warning("Evaluation contains raw text. This may indicate an error in the evaluation process.")
        st.code(evaluation["raw_response"], language="json")
        return
    
    # Check if evaluation is empty
    if not isinstance(evaluation, dict) or not evaluation:
        st.warning("No evaluation data available.")
        return
    
    # Display evaluation assessment
    if "evaluation" in evaluation:
        st.subheader("Roadmap Assessment")
        
        if isinstance(evaluation["evaluation"], dict):
            # Create cards for each criterion
            col1, col2 = st.columns(2)
            criteria = list(evaluation["evaluation"].items())
            half = len(criteria) // 2 + (1 if len(criteria) % 2 != 0 else 0)
            
            for i, (criterion, assessment) in enumerate(criteria):
                criterion_name = criterion.replace("_", " ").title()
                with col1 if i < half else col2:
                    st.markdown(f"""
                    <div style="padding: 10px; margin-bottom: 10px; border-radius: 5px; 
                                background-color: #f0f4f8; border-left: 4px solid #2196F3;">
                        <h4 style="margin: 0;">{criterion_name}</h4>
                        <p style="margin: 5px 0 0 0;">{assessment}</p>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            # Handle case where evaluation is a string or other format
            st.markdown(f"""
            <div style="padding: 15px; border-radius: 5px; background-color: #f0f4f8;">
                {evaluation["evaluation"]}
            </div>
            """, unsafe_allow_html=True)
    
    # Display suggested improvements
    if "suggested_improvements" in evaluation and evaluation["suggested_improvements"]:
        st.subheader("Suggested Improvements")
        
        improvements = evaluation["suggested_improvements"]
        if isinstance(improvements, list) and improvements:
            for i, improvement in enumerate(improvements):
                st.markdown(f"""
                <div style="padding: 10px; margin-bottom: 10px; border-radius: 5px; 
                            background-color: rgba(255, 193, 7, 0.1); border-left: 4px solid #FFC107;">
                    <b>{i+1}.</b> {improvement}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.write(improvements)

def display_cv_analysis(analysis):
    """Display the CV analysis results with better formatting"""
    if "error" in analysis:
        st.error(f"Error in analysis: {analysis['error']}")
        return
    
    if "raw_response" in analysis:
        # Try to parse JSON from raw response
        try:
            raw_text = analysis["raw_response"]
            if isinstance(raw_text, str) and "{" in raw_text:
                start_idx = raw_text.find("{")
                end_idx = raw_text.rfind("}") + 1
                if start_idx >= 0 and end_idx > start_idx:
                    json_str = raw_text[start_idx:end_idx]
                    parsed_analysis = json.loads(json_str)
                    if isinstance(parsed_analysis, dict) and len(parsed_analysis) > 0:
                        st.success("Successfully parsed analysis data")
                        return display_cv_analysis(parsed_analysis)
        except json.JSONDecodeError:
            pass
            
        st.warning("Analysis contains raw text. Displaying as is:")
        st.write(analysis["raw_response"])
        return
    
    # Display skills match
    if "skills_match" in analysis and analysis["skills_match"]:
        st.subheader("🎯 Skills Match")
        
        # Create a dataframe for skills match with confidence levels
        if isinstance(analysis["skills_match"], list):
            match_data = []
            for item in analysis["skills_match"]:
                if isinstance(item, dict) and "skill" in item and "confidence" in item:
                    match_data.append(item)
                elif isinstance(item, str):
                    # Try to parse confidence from string format
                    parts = item.split(":")
                    if len(parts) == 2:
                        skill = parts[0].strip()
                        confidence = parts[1].strip()
                        match_data.append({"skill": skill, "confidence": confidence})
                    else:
                        match_data.append({"skill": item, "confidence": "medium"})
            
            if match_data:
                df = pd.DataFrame(match_data)
                
                # Custom formatter for confidence
                def highlight_confidence(val):
                    if "high" in val.lower():
                        return "background-color: #d4edda; color: #155724"
                    elif "medium" in val.lower():
                        return "background-color: #fff3cd; color: #856404"
                    elif "low" in val.lower():
                        return "background-color: #f8d7da; color: #721c24"
                    return ""
                
                # Display styled dataframe
                st.dataframe(df.style.applymap(highlight_confidence, subset=['confidence']))
            else:
                for item in analysis["skills_match"]:
                    st.write(f"- {item}")
        else:
            st.write(analysis["skills_match"])
    
    # Display skills gap
    if "skills_gap" in analysis and analysis["skills_gap"]:
        st.subheader("🔍 Skills Gap")
        
        # Create a highlighted list of missing skills
        for skill in analysis["skills_gap"]:
            st.markdown(f"""
            <div style="padding: 10px; margin-bottom: 8px; border-radius: 5px; 
                        background-color: #f8d7da; border-left: 4px solid #dc3545;">
                {skill}
            </div>
            """, unsafe_allow_html=True)
    
    # Display recommendations
    if "recommendations" in analysis and analysis["recommendations"]:
        st.subheader("💡 Recommended Actions")
        
        # Create action cards
        for i, rec in enumerate(analysis["recommendations"]):
            st.markdown(f"""
            <div style="padding: 15px; margin-bottom: 10px; border-radius: 5px; 
                        background-color: #e8f4f8; border-left: 4px solid #17a2b8;">
                <b>Action {i+1}:</b> {rec}
            </div>
            """, unsafe_allow_html=True)
    
    # Display CV improvement suggestions
    if "cv_improvement" in analysis and analysis["cv_improvement"]:
        st.subheader("📝 Resume Improvement Tips")
        
        if isinstance(analysis["cv_improvement"], list):
            for tip in analysis["cv_improvement"]:
                st.markdown(f"""
                <div style="padding: 10px; margin-bottom: 8px; border-radius: 5px; 
                            background-color: #d1ecf1; border-left: 4px solid #0c5460;">
                    {tip}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="padding: 15px; border-radius: 5px; background-color: #d1ecf1;">
                {analysis["cv_improvement"]}
            </div>
            """, unsafe_allow_html=True)

def qa_section(roadmap, skills):
    """Create an interactive Q&A section"""
    st.header("Ask Questions About Your Roadmap")
    st.write("You can ask questions about specific skills, resources, or career advice related to your roadmap.")
    
    # Add some example questions to help users get started
    with st.expander("Example questions you can ask"):
        st.markdown("- What are the most important skills I should focus on first?")
        st.markdown("- How long will it take to complete this learning roadmap?")
        st.markdown("- What projects should I build to demonstrate my skills?")
        st.markdown("- Which certification would be most valuable for this role?")
        st.markdown("- How should I prepare for technical interviews?")
    
    question = st.text_input("Your question:", key="qa_input")
    
    if st.button("Ask Question", key="ask_btn"):
        if question:
            with st.spinner("Generating answer..."):
                try:
                    response = answer_question(question, roadmap, skills)
                    if "error" in response:
                        st.error(f"Error: {response['error']}")
                    else:
                        st.subheader("Answer:")
                        st.markdown(response["answer"])
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.warning("Please enter a question first.")

def main():
    """Main Streamlit application"""
    
    # Create sidebar
    with st.sidebar:
        st.title("Career Roadmap Generator")
        st.write("This application helps you analyze job descriptions and create personalized learning roadmaps.")
        
        st.subheader("How it works")
        st.write("1. Paste a job description")
        st.write("2. The AI extracts required skills")
        st.write("3. A customized learning roadmap is generated")
        st.write("4. Ask questions about your roadmap")
        
        st.markdown("---")
        st.info("Note: This app uses the Gemini API with free tier limits. There might be delays or occasional errors.")
    
    # Main content
    st.title("Career Roadmap Generator")
    st.write("Paste a job description below to generate your personalized learning roadmap.")
    
    # Input for job description
    job_description = st.text_area("Job Description:", height=200)
    
    # Sample job description button
    if st.button("Use Sample Job Description"):
        job_description = """
        Senior Data Scientist
        
        Job Description:
        We are seeking an experienced Data Scientist to join our analytics team. The ideal candidate will have a strong background in statistical analysis, machine learning, and data visualization.
        
        Requirements:
        - Master's degree or PhD in Data Science, Computer Science, Statistics, or related field
        - 5+ years of experience with Python, R, or similar programming languages
        - Strong understanding of machine learning algorithms and statistical modeling
        - Experience with SQL and NoSQL databases
        - Familiarity with big data technologies (Hadoop, Spark)
        - Excellent communication skills and ability to explain complex concepts to non-technical stakeholders
        - Experience with data visualization tools like Tableau or Power BI
        
        Responsibilities:
        - Develop and implement machine learning models to solve business problems
        - Collaborate with cross-functional teams to identify opportunities for data-driven insights
        - Create dashboards and visualizations to communicate findings
        - Mentor junior data scientists and analysts
        """
        st.session_state.job_description = job_description
    
    # Process button
    col1, col2 = st.columns([1, 3])
    with col1:
        generate_button = st.button("Generate Roadmap", use_container_width=True)
    
    if generate_button:
        if job_description:
            with st.spinner("Processing job description and generating roadmap..."):
                try:
                    # Process the job description
                    results = process_job_description_streamlit(job_description)
                    
                    # Store results in session state for persistence
                    st.session_state.results = results
                    st.success("Roadmap generated successfully!")
                    
                    # Automatically scroll to results
                    st.markdown('<a name="results"></a>', unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(f"Error processing job description: {str(e)}")
        else:
            st.warning("Please enter a job description first.")
    
    # Display results if available
    if 'results' in st.session_state:
        results = st.session_state.results
        
        st.markdown("---")
        st.markdown("<h1 style='text-align: center; color: #4CAF50;'>Career Roadmap Analysis</h1>", unsafe_allow_html=True)
        
        # Job stats with more visual elements
        st.subheader("Job Description Stats")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Word Count", results["jd_data"]["word_count"], 
                     delta=f"{results['jd_data']['word_count'] - 150}" if results['jd_data']['word_count'] > 150 else None,
                     delta_color="normal")
        with col2:
            st.metric("Character Count", results["jd_data"]["char_count"])
        
        # Visual separator
        st.markdown("---")
        
        # Create tabs with icons - add a new tab for CV analysis
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "💼 Extracted Skills", 
            "🛣️ Learning Roadmap", 
            "📊 Evaluation", 
            "📄 CV Analysis",
            "❓ Q&A"
        ])
        
        with tab1:
            st.header("Extracted Skills")
            if "skills_data" in results:
                display_skills(results["skills_data"])
            else:
                st.error("No skills data available")
        
        with tab2:
            st.header("Learning Roadmap")
            if "improved_roadmap" in results and results["improved_roadmap"]:
                display_roadmap(results["improved_roadmap"])
            else:
                st.error("No roadmap data available")
        
        with tab3:
            st.header("Roadmap Evaluation")
            if "evaluation_data" in results:
                display_evaluation(results["evaluation_data"])
            else:
                st.error("No evaluation data available")
        
        with tab4:
            st.header("CV/Resume Analysis")
            st.write("Upload your CV/resume to get personalized feedback based on the job requirements and roadmap.")
            
            # Create a button to clear the uploaded file if needed
            if 'uploaded_cv' in st.session_state and st.button("Clear uploaded file"):
                del st.session_state.uploaded_cv
                st.experimental_rerun()
            
            # Use the file_uploader, but store the result in session state
            uploaded_file = st.file_uploader("Upload your CV/Resume (PDF)", type="pdf", key="cv_uploader")
            
            # If we have a new upload, store it in session state
            if uploaded_file is not None:
                st.session_state.uploaded_cv = uploaded_file
            
            # Use the file from session state for processing, if available
            if 'uploaded_cv' in st.session_state:
                try:
                    # Use the file from session state
                    cv_file = st.session_state.uploaded_cv
                    
                    # Show a preview of the file name and size
                    file_details = {"Filename": cv_file.name, "FileSize": f"{cv_file.size/1024:.2f} KB"}
                    
                    # Extract text from the PDF
                    with st.spinner("Extracting text from PDF..."):
                        # Store extracted text in session state if not already there
                        if 'cv_text' not in st.session_state:
                            st.session_state.cv_text = extract_text_from_pdf(cv_file.getvalue())
                        cv_text = st.session_state.cv_text
                    
                    # Show text extraction result
                    with st.expander("Extracted Text Preview"):
                        st.text(cv_text[:500] + ("..." if len(cv_text) > 500 else ""))
                        st.write(f"Total characters: {len(cv_text)}")
                    
                    # Analyze CV button
                    if st.button("Analyze CV Against Job Requirements"):
                        with st.spinner("Analyzing your CV against job requirements..."):
                            analysis_result = analyze_cv(
                                cv_text=cv_text,
                                skills=results["skills_data"],
                                roadmap=results["improved_roadmap"]
                            )
                            
                            # Store in session state
                            st.session_state.cv_analysis = analysis_result
                    
                    # Display analysis if available
                    if "cv_analysis" in st.session_state:
                        display_cv_analysis(st.session_state.cv_analysis)
                        
                        # Offer download of analysis
                        analysis_json = json.dumps(st.session_state.cv_analysis, indent=2)
                        st.download_button(
                            label="Download Analysis (JSON)",
                            data=analysis_json,
                            file_name="cv_analysis.json",
                            mime="application/json"
                        )
                
                except Exception as e:
                    st.error(f"Error processing CV: {str(e)}")
            else:
                st.info("Please upload a PDF file to begin the analysis.")
        
        with tab5:
            if "improved_roadmap" in results and "skills_data" in results:
                qa_section(results["improved_roadmap"], results["skills_data"])
            else:
                st.error("Required data not available for Q&A")
        
        # Download options
        st.markdown("---")
        st.subheader("Download Results")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            skills_path = os.path.join(results["output_dir"], "extracted_skills.json")
            with open(skills_path, "r") as file:
                skills_json = file.read()
            st.download_button(
                label="Download Skills (JSON)",
                data=skills_json,
                file_name="extracted_skills.json",
                mime="application/json"
            )
        
        with col2:
            roadmap_path = os.path.join(results["output_dir"], "final_roadmap.json")
            with open(roadmap_path, "r") as file:
                roadmap_json = file.read()
            st.download_button(
                label="Download Roadmap (JSON)",
                data=roadmap_json,
                file_name="career_roadmap.json",
                mime="application/json"
            )
        
        with col3:
            # Create a markdown version of the roadmap for download
            roadmap_md = f"# Career Learning Roadmap\n\n"
            roadmap_md += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
            
            for phase, data in results["improved_roadmap"].items():
                if isinstance(data, dict):
                    roadmap_md += f"## {phase}\n\n"
                    
                    if "skills" in data and data["skills"]:
                        roadmap_md += "### Skills to Focus On\n\n"
                        for skill in data["skills"]:
                            roadmap_md += f"- {skill}\n"
                        roadmap_md += "\n"
                    
                    if "resources" in data and data["resources"]:
                        roadmap_md += "### Recommended Resources\n\n"
                        for resource in data["resources"]:
                            roadmap_md += f"- {resource}\n"
                        roadmap_md += "\n"
                    
                    if "projects" in data and data["projects"]:
                        roadmap_md += "### Projects & Exercises\n\n"
                        for project in data["projects"]:
                            roadmap_md += f"- {project}\n"
                        roadmap_md += "\n"
                    
                    if "estimated_time" in data:
                        roadmap_md += f"### Estimated Time: {data['estimated_time']}\n\n"
            
            st.download_button(
                label="Download Roadmap (Markdown)",
                data=roadmap_md,
                file_name="career_roadmap.md",
                mime="text/markdown"
            )

if __name__ == "__main__":
    main()
