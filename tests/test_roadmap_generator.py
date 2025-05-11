import unittest
import os
import sys
import json
import tempfile
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from roadmap_generator import generate_roadmap, load_input, save_output

class TestRoadmapGenerator(unittest.TestCase):
    
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
                "skills": ["Machine Learning basics", "Data visualization"],
                "resources": ["Machine Learning course"],
                "projects": ["ML project with scikit-learn"],
                "estimated_time": "8 weeks"
            },
            "Specialization Phase": {
                "skills": ["Advanced ML techniques"],
                "resources": ["Deep Learning specialization"],
                "projects": ["End-to-end ML project"],
                "estimated_time": "12 weeks"
            }
        }
        
        self.temp_dir = tempfile.TemporaryDirectory()
        
    def tearDown(self):
        self.temp_dir.cleanup()
    
    @patch('roadmap_generator.generate_content')
    def test_generate_roadmap(self, mock_generate_content):
        # Setup mock to return our predefined roadmap
        mock_generate_content.return_value = json.dumps(self.sample_roadmap)
        
        # Call function with our sample skills
        result = generate_roadmap(self.sample_skills)
        
        # Verify results
        self.assertEqual(result, self.sample_roadmap)
        mock_generate_content.assert_called_once()
        
        # Verify the prompt contains skills data
        args = mock_generate_content.call_args[1]
        self.assertIn("prompt", args)
        for skill in self.sample_skills["Technical Skills"]:
            self.assertIn(skill, args["prompt"])
    
    @patch('roadmap_generator.generate_content')
    def test_generate_roadmap_error(self, mock_generate_content):
        # Setup mock to raise an exception
        mock_generate_content.side_effect = Exception("API error")
        
        # Call function
        result = generate_roadmap(self.sample_skills)
        
        # Verify error handling
        self.assertIn("error", result)
        self.assertEqual(result["error"], "API error")
    
    def test_load_input(self):
        # Create a temporary skills file
        skills_file = os.path.join(self.temp_dir.name, "skills.json")
        with open(skills_file, 'w') as f:
            json.dump(self.sample_skills, f)
        
        # Test loading the file
        result = load_input(skills_file)
        self.assertEqual(result, self.sample_skills)
        
        # Test file not found
        with self.assertRaises(FileNotFoundError):
            load_input("nonexistent_file.json")
    
    def test_save_output(self):
        output_path = os.path.join(self.temp_dir.name, "roadmap.json")
        
        # Test saving to file
        result = save_output(self.sample_roadmap, output_path)
        self.assertTrue(os.path.exists(output_path))
        
        # Verify saved data
        with open(output_path, 'r') as f:
            saved_data = json.load(f)
        self.assertEqual(saved_data, self.sample_roadmap)
        
        # Test return as string
        result = save_output(self.sample_roadmap)
        self.assertIsInstance(result, str)
        parsed_result = json.loads(result)
        self.assertEqual(parsed_result, self.sample_roadmap)

if __name__ == '__main__':
    unittest.main()
