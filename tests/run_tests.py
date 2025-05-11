import unittest
import sys
import os

# Add the parent directory to the Python path for importing modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import test modules
from tests.test_job_description_handler import TestJobDescriptionHandler
from tests.test_api_utils import TestApiUtils
from tests.test_skill_extractor import TestSkillExtractor
from tests.test_roadmap_generator import TestRoadmapGenerator
from tests.test_response_critic import TestResponseCritic
from tests.test_qa_assistant import TestQaAssistant
from tests.test_pipeline import TestPipeline

def create_test_suite():
    """Create a test suite including all test cases"""
    test_suite = unittest.TestSuite()
    
    # Add test cases from each module
    test_suite.addTest(unittest.makeSuite(TestJobDescriptionHandler))
    test_suite.addTest(unittest.makeSuite(TestApiUtils))
    test_suite.addTest(unittest.makeSuite(TestSkillExtractor))
    test_suite.addTest(unittest.makeSuite(TestRoadmapGenerator))
    test_suite.addTest(unittest.makeSuite(TestResponseCritic))
    test_suite.addTest(unittest.makeSuite(TestQaAssistant))
    test_suite.addTest(unittest.makeSuite(TestPipeline))
    
    return test_suite

if __name__ == '__main__':
    # Create a test runner
    runner = unittest.TextTestRunner(verbosity=2)
    # Run all tests
    suite = create_test_suite()
    result = runner.run(suite)
    
    # Exit with non-zero code if tests failed
    sys.exit(not result.wasSuccessful())
