import unittest
import os
import sys
import json
import tempfile
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from skill_extractor import extract_skills, load_input, save_output

class TestSkillExtractor(unittest.TestCase):
    
    def setUp(self):
        self.sample_jd = """
        Senior Data Scientist with 5+ years experience.
        Requirements:
        - Python
        - Machine Learning
        - SQL
        - Communication Skills
        """
        self.temp_dir = tempfile.TemporaryDirectory()
        
        # Sample skills that would be returned by the API
        self.sample_skills = {
            "Technical Skills": ["Python", "Machine Learning", "SQL"],
            "Soft Skills": ["Communication Skills"],
            "Domain-Specific Skills": [],
            "Certifications": [],
            "Experience Requirements": ["5+ years experience"]
        }
        
    def tearDown(self):
        self.temp_dir.cleanup()
    
    @patch('skill_extractor.generate_content')
    def test_extract_skills(self, mock_generate_content):
        # Setup the mock to return our predefined skills
        mock_generate_content.return_value = json.dumps(self.sample_skills)
        
        # Call the function with our sample job description
        result = extract_skills(self.sample_jd)
        
        # Verify results
        self.assertEqual(result, self.sample_skills)
        mock_generate_content.assert_called_once()
        
        # Check what prompt was sent to the LLM
        args = mock_generate_content.call_args[1]
        self.assertIn("prompt", args)
        self.assertIn(self.sample_jd, args["prompt"])
    
    @patch('skill_extractor.generate_content')
    def test_extract_skills_error(self, mock_generate_content):
        # Setup mock to raise an exception
        mock_generate_content.side_effect = Exception("API error")
        
        # Call function
        result = extract_skills(self.sample_jd)
        
        # Verify error handling
        self.assertIn("error", result)
        self.assertEqual(result["error"], "API error")
    
    def test_load_input(self):
        # Create a temporary input file
        input_data = {"job_description": self.sample_jd}
        input_file = os.path.join(self.temp_dir.name, "input.json")
        with open(input_file, 'w') as f:
            json.dump(input_data, f)
        
        # Test loading the file
        result = load_input(input_file)
        self.assertEqual(result, self.sample_jd)
        
        # Test file not found
        with self.assertRaises(FileNotFoundError):
            load_input("nonexistent_file.json")
    
    def test_save_output(self):
        output_path = os.path.join(self.temp_dir.name, "skills.json")
        
        # Test saving to file
        result = save_output(self.sample_skills, output_path)
        self.assertTrue(os.path.exists(output_path))
        
        # Verify saved data
        with open(output_path, 'r') as f:
            saved_data = json.load(f)
        self.assertEqual(saved_data, self.sample_skills)
        
        # Test return as string
        result = save_output(self.sample_skills)
        self.assertIsInstance(result, str)
        parsed_result = json.loads(result)
        self.assertEqual(parsed_result, self.sample_skills)

if __name__ == '__main__':
    unittest.main()
