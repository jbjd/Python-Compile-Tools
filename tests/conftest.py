"""Common file for pytest framework to define test fixtures, also used to
define other constants used within tests"""

import os

WORKING_DIR: str = os.path.dirname(__file__)
EXAMPLE_FOLDER: str = os.path.join(WORKING_DIR, "test_folder")
REQUIREMENTS_FOLDER: str = os.path.join(WORKING_DIR, "requirements_examples")
