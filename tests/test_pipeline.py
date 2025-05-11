import unittest
import os
import sys
import json
import tempfile
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline import run_pipeline, create_session_folder

class TestPipeline(unittest.TestCase):
    
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.sample_jd = """
        Senior Data Scientist
        Requirements:
        - Python
        - Machine Learning
        """
        
        # Create a temporary job description file
        self.jd_file = os.path.join(self.temp_dir.name, "jd.txt")
        with open(self.jd_file, 'w') as f:
            f.write(self.sample_jd)
            
        # Sample results for mocking component functions
        self.sample_jd_result = {
            "job_description": self.sample_jd.strip(),
            "word_count": 5,
            "char_count": 50
        }
        
        self.sample_skills = {
            "Technical Skills": ["Python", "Machine Learning"],
            "Soft Skills": [],
            "Domain-Specific Skills": [],
            "Certifications": [],
            "Experience Requirements": []
        }
        
        self.sample_roadmap = {
            "Foundation Phase": {
                "skills": ["Python basics"],
                "resources": ["Python Course"],
                "projects": ["Simple project"],
                "estimated_time": "4 weeks"
            }
        }
        
        self.sample_evaluation = {
            "evaluation": "Good roadmap",
            "suggested_improvements": ["Add more details"],
            "improved_roadmap": {
                "Foundation Phase": {
                    "skills": ["Python basics"],
                    "resources": ["Python Course", "Extra resource"],
                    "projects": ["Simple project"],
                    "estimated_time": "4 weeks"
                }
            }
        }
        
    def tearDown(self):
        self.temp_dir.cleanup()
    
    def test_create_session_folder(self):
        # Patch the OUTPUT_DIR to use our temp directory
        with patch('pipeline.OUTPUT_DIR', self.temp_dir.name):
            session_dir = create_session_folder()
            self.assertTrue(os.path.exists(session_dir))
            self.assertTrue(session_dir.startswith(self.temp_dir.name))
    
    @patch('pipeline.process_job_description')
    @patch('pipeline.extract_skills')
    @patch('pipeline.generate_roadmap')
    @patch('pipeline.evaluate_roadmap')
    @patch('pipeline.interactive_mode')
    @patch('pipeline.OUTPUT_DIR', None)  # This will be replaced in the test
    def test_run_pipeline(self, mock_interactive, mock_evaluate, mock_generate, 
                         mock_extract, mock_process):
        # Setup mocks
        mock_process.return_value = self.sample_jd_result
        mock_extract.return_value = self.sample_skills
        mock_generate.return_value = self.sample_roadmap
        mock_evaluate.return_value = self.sample_evaluation
        
        # Patch OUTPUT_DIR to use our temp directory
        with patch('pipeline.OUTPUT_DIR', self.temp_dir.name):
            # Run pipeline with text input
            results = run_pipeline(job_description=self.sample_jd, output_dir=self.temp_dir.name)
            
            # Verify all components were called
            mock_process.assert_called_once()
            mock_extract.assert_called_once()
            mock_generate.assert_called_once()
            mock_evaluate.assert_called_once()
            
            # Verify results and files
            self.assertEqual(results["output_dir"], self.temp_dir.name)
            self.assertTrue(os.path.exists(results["job_description_path"]))
            self.assertTrue(os.path.exists(results["skills_path"]))
            self.assertTrue(os.path.exists(results["roadmap_path"]))
            self.assertTrue(os.path.exists(results["evaluation_path"]))
            self.assertTrue(os.path.exists(results["final_roadmap_path"]))
            
            # Test with file input and interactive mode
            mock_process.reset_mock()
            mock_extract.reset_mock()
            mock_generate.reset_mock()
            mock_evaluate.reset_mock()
            mock_interactive.reset_mock()
            
            results = run_pipeline(jd_file=self.jd_file, interactive=True)
            
            # Verify file input works
            mock_process.assert_called_once_with(None, self.jd_file)
            
            # Verify interactive mode was called
            mock_interactive.assert_called_once()
    
    @patch('pipeline.process_job_description')
    @patch('pipeline.extract_skills')
    @patch('pipeline.generate_roadmap')
    @patch('pipeline.evaluate_roadmap')
    @patch('pipeline.OUTPUT_DIR', None)
    def test_run_pipeline_with_errors(self, mock_evaluate, mock_generate, 
                                     mock_extract, mock_process):
        # Setup mocks with error in skill extraction
        mock_process.return_value = self.sample_jd_result
        mock_extract.return_value = {"error": "API error"}
        mock_generate.return_value = self.sample_roadmap
        mock_evaluate.return_value = self.sample_evaluation
        
        # Patch OUTPUT_DIR to use our temp directory
        with patch('pipeline.OUTPUT_DIR', self.temp_dir.name):
            # Run pipeline
            results = run_pipeline(job_description=self.sample_jd, output_dir=self.temp_dir.name)
            
            # Verify pipeline continues despite extraction error
            mock_generate.assert_called_once()
            self.assertTrue(os.path.exists(results["skills_path"]))
            
            # Setup error in evaluation
            mock_extract.return_value = self.sample_skills
            mock_evaluate.side_effect = Exception("API error")
            
            # Run pipeline again
            results = run_pipeline(job_description=self.sample_jd, output_dir=self.temp_dir.name)
            
            # Verify pipeline handles evaluation error
            self.assertTrue(os.path.exists(results["evaluation_path"]))

if __name__ == '__main__':
    unittest.main()
