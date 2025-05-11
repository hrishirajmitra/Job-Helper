import unittest
import os
import sys
import json
import tempfile
from unittest.mock import patch, MagicMock, mock_open

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qa_assistant import answer_question, load_input

class TestQaAssistant(unittest.TestCase):
    
    def setUp(self):
        self.sample_roadmap = {
            "Foundation Phase": {
                "skills": ["Python basics", "SQL fundamentals"],
                "resources": ["Coursera Python Course", "SQL Tutorial"],
                "projects": ["Data analysis project"],
                "estimated_time": "4 weeks"
            },
            "Development Phase": {
                "skills": ["Machine Learning basics", "Data visualization"],
                "resources": ["Machine Learning course"],
                "projects": ["ML project"],
                "estimated_time": "8 weeks"
            }
        }
        
        self.sample_skills = {
            "Technical Skills": ["Python", "Machine Learning", "SQL"],
            "Soft Skills": ["Communication Skills"],
            "Domain-Specific Skills": [],
            "Certifications": [],
            "Experience Requirements": ["5+ years experience"]
        }
        
        self.sample_question = "What skills should I learn first?"
        self.sample_answer = "You should start with Python basics and SQL fundamentals as mentioned in the Foundation Phase of your roadmap. These are core skills that will provide the basis for more advanced topics."
        
        self.temp_dir = tempfile.TemporaryDirectory()
        
    def tearDown(self):
        self.temp_dir.cleanup()
    
    @patch('qa_assistant.generate_content')
    def test_answer_question(self, mock_generate_content):
        # Setup mock to return our predefined answer
        mock_generate_content.return_value = self.sample_answer
        
        # Call function with our sample question, roadmap, and skills
        result = answer_question(self.sample_question, self.sample_roadmap, self.sample_skills)
        
        # Verify results
        self.assertEqual(result["question"], self.sample_question)
        self.assertEqual(result["answer"], self.sample_answer)
        mock_generate_content.assert_called_once()
        
        # Verify the prompt contains question, roadmap and optionally skills
        args = mock_generate_content.call_args[1]
        self.assertIn("prompt", args)
        self.assertIn(self.sample_question, args["prompt"])
        self.assertIn("Roadmap", args["prompt"])
        self.assertIn("Extracted Skills", args["prompt"])
    
    @patch('qa_assistant.generate_content')
    def test_answer_question_without_skills(self, mock_generate_content):
        # Setup mock
        mock_generate_content.return_value = self.sample_answer
        
        # Call function without skills
        result = answer_question(self.sample_question, self.sample_roadmap)
        
        # Verify skills parameter is optional
        self.assertEqual(result["answer"], self.sample_answer)
        
        # Verify prompt doesn't contain skills section
        args = mock_generate_content.call_args[1]
        prompt = args["prompt"]
        self.assertNotIn("Extracted Skills:", prompt)
    
    @patch('qa_assistant.generate_content')
    def test_answer_question_error(self, mock_generate_content):
        # Setup mock to raise an exception
        mock_generate_content.side_effect = Exception("API error")
        
        # Call function
        result = answer_question(self.sample_question, self.sample_roadmap)
        
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
        
        # Test loading with both files
        roadmap, skills = load_input(roadmap_file, skills_file)
        self.assertEqual(roadmap, self.sample_roadmap)
        self.assertEqual(skills, self.sample_skills)
        
        # Test loading without skills file
        roadmap, skills = load_input(roadmap_file)
        self.assertEqual(roadmap, self.sample_roadmap)
        self.assertIsNone(skills)
        
        # Test with nonexistent roadmap file
        with self.assertRaises(FileNotFoundError):
            load_input("nonexistent_file.json")

if __name__ == '__main__':
    unittest.main()
