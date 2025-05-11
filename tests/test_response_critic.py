import unittest
import os
import sys
import json
import tempfile
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from response_critic import evaluate_roadmap, load_input, save_output

class TestResponseCritic(unittest.TestCase):
    
    def setUp(self):
        self.sample_skills = {
            "Technical Skills": ["Python", "Machine Learning", "SQL"],
            "Soft Skills": ["Communication Skills"],
            "Domain-Specific Skills": [],
            "Certifications": [],
            "Experience Requirements": ["5+ years experience"]
        }
        
        self.sample_roadmap = {
            "Foundation Phase": {
                "skills": ["Python basics", "SQL fundamentals"],
                "resources": ["Coursera Python Course", "SQL Tutorial"],
                "projects": ["Data analysis project"],
                "estimated_time": "4 weeks"
            },
            "Development Phase": {
                "skills": ["Machine Learning basics"],
                "resources": ["Machine Learning course"],
                "projects": ["ML project"],
                "estimated_time": "8 weeks"
            }
        }
        
        self.sample_evaluation = {
            "evaluation": {
                "coverage": "Good coverage of technical skills",
                "relevance": "Highly relevant to the job role",
                "structure": "Well structured with clear progression",
                "practicality": "Realistic timeline and resources",
                "completeness": "Could include more detail on ML techniques"
            },
            "suggested_improvements": [
                "Add more advanced ML techniques in Specialization phase",
                "Include more resources for data visualization"
            ],
            "improved_roadmap": {
                "Foundation Phase": {
                    "skills": ["Python basics", "SQL fundamentals"],
                    "resources": ["Coursera Python Course", "SQL Tutorial"],
                    "projects": ["Data analysis project"],
                    "estimated_time": "4 weeks"
                },
                "Development Phase": {
                    "skills": ["Machine Learning basics", "Data visualization"],
                    "resources": ["Machine Learning course", "Data Viz course"],
                    "projects": ["ML project with visualization"],
                    "estimated_time": "8 weeks"
                },
                "Specialization Phase": {
                    "skills": ["Advanced ML", "Deep Learning"],
                    "resources": ["Deep Learning Specialization"],
                    "projects": ["End-to-end ML project"],
                    "estimated_time": "10 weeks"
                }
            }
        }
        
        self.temp_dir = tempfile.TemporaryDirectory()
        
    def tearDown(self):
        self.temp_dir.cleanup()
    
    @patch('response_critic.generate_content')
    def test_evaluate_roadmap(self, mock_generate_content):
        # Setup mock to return our predefined evaluation
        mock_generate_content.return_value = json.dumps(self.sample_evaluation)
        
        # Call function with our sample roadmap and skills
        result = evaluate_roadmap(self.sample_roadmap, self.sample_skills)
        
        # Verify results
        self.assertEqual(result, self.sample_evaluation)
        mock_generate_content.assert_called_once()
        
        # Verify the prompt contains roadmap and skills data
        args = mock_generate_content.call_args[1]
        self.assertIn("prompt", args)
        self.assertIn("Original Skills", args["prompt"])
        self.assertIn("Generated Roadmap", args["prompt"])
    
    @patch('response_critic.generate_content')
    def test_evaluate_roadmap_error(self, mock_generate_content):
        # Setup mock to raise an exception
        mock_generate_content.side_effect = Exception("API error")
        
        # Call function
        result = evaluate_roadmap(self.sample_roadmap, self.sample_skills)
        
        # Verify error handling
        self.assertIn("error", result)
        self.assertEqual(result["error"], "API error")
    
    def test_load_input(self):
        # Create temporary files
        roadmap_file = os.path.join(self.temp_dir.name, "roadmap.json")
        skills_file = os.path.join(self.temp_dir.name, "skills.json")
        
        with open(roadmap_file, 'w') as f:
            json.dump(self.sample_roadmap, f)
        
        with open(skills_file, 'w') as f:
            json.dump(self.sample_skills, f)
        
        # Test loading the files
        roadmap, skills = load_input(roadmap_file, skills_file)
        self.assertEqual(roadmap, self.sample_roadmap)
        self.assertEqual(skills, self.sample_skills)
        
        # Test file not found
        with self.assertRaises(FileNotFoundError):
            load_input("nonexistent_roadmap.json", skills_file)
            
        with self.assertRaises(FileNotFoundError):
            load_input(roadmap_file, "nonexistent_skills.json")
    
    def test_save_output(self):
        output_path = os.path.join(self.temp_dir.name, "evaluation.json")
        
        # Test saving to file
        result = save_output(self.sample_evaluation, output_path)
        self.assertTrue(os.path.exists(output_path))
        
        # Verify saved data
        with open(output_path, 'r') as f:
            saved_data = json.load(f)
        self.assertEqual(saved_data, self.sample_evaluation)
        
        # Test return as string
        result = save_output(self.sample_evaluation)
        self.assertIsInstance(result, str)
        parsed_result = json.loads(result)
        self.assertEqual(parsed_result, self.sample_evaluation)

if __name__ == '__main__':
    unittest.main()
