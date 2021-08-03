import unittest
import json
import os
from pathlib import Path

# define constant path to test data file
test_data_file_path = str(Path(os.path.dirname(os.path.dirname(__file__)), 'data', 'test_event.json'))


class TestSum(unittest.TestCase):
    def setUp(self):
        self.test_data_file_path = str(Path(os.path.dirname(os.path.dirname(__file__)), 'data', 'test_event.json'))

    def test_event_json_file(self):
        try:
            with open(self.test_data_file_path, "rb") as read_file:
                json.load(read_file)
            isvalid_json = True
        except ValueError as e:
            isvalid_json = False

        self.assertTrue(isvalid_json, self.test_data_file_path)


if __name__ == '__main__':
    unittest.main()
