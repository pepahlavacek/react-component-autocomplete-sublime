import unittest
import os
import re
from ReactAutocomplete.output import *

import sublime
import sys

version = sublime.version()

class TestOutput(unittest.TestCase):

    # test jsx parsing
    def test_string(self):
        result = get_value_for_type("string", "JSX")
        
        self.assertEqual(result, '""')

if __name__ == '__main__':
  unittest.main()