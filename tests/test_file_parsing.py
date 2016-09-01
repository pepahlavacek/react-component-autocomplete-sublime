import unittest
import os
import re
from ReactComponentAutocomplete.parsing import *

import sublime
import sys


version = sublime.version()

STUB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stubs")

class TestFileParsing(unittest.TestCase):

    # test jsx parsing
    def test_jsx(self):
      with open(os.path.join(STUB_PATH, "stub-jsx.jsx"), 'r') as f:
        component_info = get_file_info(f)
        self.assertEqual(component_info["display_name"], "AriaStatus")
        self.assertEqual(component_info["props"][0]["name"], "message")
        self.assertEqual(component_info["props"][0]["type"], "string")
        self.assertEqual(component_info["props"][0]["is_required"], False)

    def test_jsx_two(self):
      with open(os.path.join(STUB_PATH, "stub-jsx2.jsx"), 'r') as f:
        component_info = get_file_info(f)
        self.assertEqual(component_info["display_name"], "CheckboxGroup")
        self.assertEqual(component_info["props"][0]["name"], "name")
        self.assertEqual(component_info["props"][0]["type"], "string")
        self.assertEqual(component_info["props"][0]["is_required"], True)
        self.assertEqual(component_info["props"][1]["name"], "options")
        self.assertEqual(component_info["props"][1]["type"], "array")
        self.assertEqual(component_info["props"][1]["is_required"], True)

    def test_js(self):
      with open(os.path.join(STUB_PATH, "stub-js.js"), 'r') as f:
        component_info = get_file_info(f)
        self.assertEqual(component_info["display_name"], "InputField")
        self.assertEqual(component_info["props"][0]["name"], "value")
        self.assertEqual(component_info["props"][0]["type"], "string")
        self.assertEqual(component_info["props"][0]["is_required"], False)
        self.assertEqual(component_info["props"][1]["name"], "onChange")
        self.assertEqual(component_info["props"][1]["type"], "func")
        self.assertEqual(component_info["props"][1]["is_required"], False)

    def test_display_name_with_double_quotes(self):
      with open(os.path.join(STUB_PATH, "display_name_with_double_quotes.jsx"), 'r') as f:
        component_info = get_file_info(f)

        self.assertEqual(component_info["display_name"], "ComponentName")

    def test_display_name_with_single_quotes(self):
      with open(os.path.join(STUB_PATH, "display_name_with_single_quotes.jsx"), 'r') as f:
        component_info = get_file_info(f)

        self.assertEqual(component_info["display_name"], "ComponentName")

    def test_display_name_with_comma(self):
      with open(os.path.join(STUB_PATH, "display_name_with_comma.jsx"), 'r') as f:
        component_info = get_file_info(f)

        self.assertEqual(component_info["display_name"], "ComponentName")

    def test_var_name_to_display_name(self):
      with open(os.path.join(STUB_PATH, "var_name_to_display_name.jsx"), 'r') as f:
        component_info = get_file_info(f)

        self.assertEqual(component_info["display_name"], "CheckboxGroup")

    def test_const_name_to_display_name(self):
      with open(os.path.join(STUB_PATH, "const_name_to_display_name.jsx"), 'r') as f:
        component_info = get_file_info(f)

        self.assertEqual(component_info["display_name"], "CheckboxGroup")

    def test_let_name_to_display_name(self):
      with open(os.path.join(STUB_PATH, "let_name_to_display_name.jsx"), 'r') as f:
        component_info = get_file_info(f)

        self.assertEqual(component_info["display_name"], "CheckboxGroup")

    def test_exports_name_create_class(self):
      with open(os.path.join(STUB_PATH, "exports_name_create_class.jsx"), 'r') as f:
        component_info = get_file_info(f)

        self.assertEqual(component_info["display_name"], "NavActivityFeedToggle")


    def test_stops_getting_prop_types_on_new_line(self):
      with open(os.path.join(STUB_PATH, "stops_getting_prop_types_on_new_line.jsx"), 'r') as f:
        component_info = get_file_info(f)

        self.assertEqual(component_info["display_name"], "AriaStatus")

        self.assertEqual(component_info["props"][0]["name"], "oneProp")
        self.assertEqual(component_info["props"][0]["type"], "string")
        self.assertEqual(component_info["props"][0]["is_required"], False)
        self.assertEqual(component_info["props"][1]["name"], "twoProps")
        self.assertEqual(component_info["props"][1]["type"], "string")
        self.assertEqual(component_info["props"][1]["is_required"], False)

        self.assertEqual(len(component_info["props"]), 2)


    def test_stops_getting_prop_types_on_different_key_cjsx(self):
      with open(os.path.join(STUB_PATH, "stops_getting_prop_types_on_different_key.cjsx"), 'r') as f:
        component_info = get_file_info(f)

        self.assertEqual(component_info["display_name"], "NavActivityFeedToggle")
        self.assertEqual(len(component_info["props"]), 3)

    def test_stops_getting_prop_types_on_different_key(self):
      with open(os.path.join(STUB_PATH, "stops_getting_prop_types_on_different_key.jsx"), 'r') as f:
        component_info = get_file_info(f)

        self.assertEqual(component_info["display_name"], "AriaStatus")
        self.assertEqual(len(component_info["props"]), 2)

    def test_parses_camel_case_prop(self):
      with open(os.path.join(STUB_PATH, "parses_camel_case_prop.jsx"), 'r') as f:
        component_info = get_file_info(f)

        self.assertEqual(component_info["display_name"], "CheckboxGroup")

        self.assertEqual(component_info["props"][0]["name"], "firstProp")
        self.assertEqual(component_info["props"][1]["name"], "secondProp")


    def test_parses_snake_case_prop(self):
      with open(os.path.join(STUB_PATH, "parses_snake_case_prop.jsx"), 'r') as f:
        component_info = get_file_info(f)

        self.assertEqual(component_info["display_name"], "CheckboxGroup")

        self.assertEqual(component_info["props"][0]["name"], "first_prop")
        self.assertEqual(component_info["props"][1]["name"], "second_prop")

    def test_cjsx(self):
      with open(os.path.join(STUB_PATH, "stub-cjsx.cjsx"), 'r') as f:
        component_info = get_file_info(f)
        self.assertEqual(component_info["display_name"], "NavActivityFeedToggle")

        self.assertEqual(component_info["props"][0]["name"], "isOpen")
        self.assertEqual(component_info["props"][0]["type"], "bool")
        self.assertEqual(component_info["props"][0]["is_required"], False)

        self.assertEqual(component_info["props"][1]["name"], "lastOpenedAt")
        self.assertEqual(component_info["props"][1]["type"], "number")
        self.assertEqual(component_info["props"][1]["is_required"], True)

        self.assertEqual(component_info["props"][2]["name"], "lastClosedAt")
        self.assertEqual(component_info["props"][2]["type"], "number")
        self.assertEqual(component_info["props"][2]["is_required"], False)

        self.assertEqual(component_info["props"][3]["name"], "hasNewNotifications")
        self.assertEqual(component_info["props"][3]["type"], "bool")
        self.assertEqual(component_info["props"][3]["is_required"], True)

        self.assertEqual(component_info["props"][4]["name"], "showPipe")
        self.assertEqual(component_info["props"][4]["type"], "bool")
        self.assertEqual(component_info["props"][4]["is_required"], False)

    def test_cjsx2(self):
      with open(os.path.join(STUB_PATH, "stub-cjsx2.cjsx"), 'r') as f:
        component_info = get_file_info(f)
        self.assertEqual(component_info["display_name"], "NavActivityFeedToggle")

    def test_parses_jsx_prop_types(self):
      with open(os.path.join(STUB_PATH, "parse_prop_types.jsx"), 'r') as f:
        component_info = get_file_info(f)

        self.assertEqual(component_info["display_name"], "MyComponent")
        self.assertEqual(len(component_info["props"]), 19)

if __name__ == '__main__':
  unittest.main()