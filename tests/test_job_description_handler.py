import unittest
import os
import json
import tempfile
import sys
from pathlib import Path

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from job_description_handler import process_job_description, clean_job_description, save_output

class TestJobDescriptionHandler(unittest.TestCase):
    
    def setUp(self):
        self.sample_jd = """
        Senior Data Scientist
        
        Requirements:
        - 5+ years of experience with Python
        - Strong understanding of machine learning
        """
        self.temp_dir = tempfile.TemporaryDirectory()
        
    def tearDown(self):
        self.temp_dir.cleanup()
        
    def test_clean_job_description(self):
        input_text = "  This is  a   job description  with extra   spaces.  "
        expected = "This is a job description with extra spaces."
        self.assertEqual(clean_job_description(input_text), expected)
    
    def test_process_job_description_from_text(self):
        result = process_job_description(input_text=self.sample_jd)
        self.assertIsInstance(result, dict)
        self.assertIn("job_description", result)
        self.assertIn("word_count", result)
        self.assertIn("char_count", result)
        self.assertTrue(result["word_count"] > 0)
        self.assertTrue(result["char_count"] > 0)
    
    def test_process_job_description_from_file(self):
        # Create a temporary file with job description
        temp_file = os.path.join(self.temp_dir.name, "test_jd.txt")
        with open(temp_file, 'w') as f:
            f.write(self.sample_jd)
            
        result = process_job_description(input_file=temp_file)
        self.assertIsInstance(result, dict)
        self.assertIn("job_description", result)
        self.assertEqual(clean_job_description(self.sample_jd), result["job_description"])
    
    def test_process_job_description_no_input(self):
        with self.assertRaises(ValueError):
            process_job_description()
    
    def test_save_output(self):
        data = {"test": "data"}
        output_path = os.path.join(self.temp_dir.name, "output.json")
        
        # Test saving to file
        result = save_output(data, output_path)
        self.assertTrue(os.path.exists(output_path))
        with open(output_path, 'r') as f:
            saved_data = json.load(f)
        self.assertEqual(data, saved_data)
        
        # Test returning as string
        result = save_output(data)
        self.assertIsInstance(result, str)
        self.assertEqual(json.loads(result), data)

if __name__ == '__main__':
    unittest.main()
