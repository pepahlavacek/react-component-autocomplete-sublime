import unittest
import os
import re

STUB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stubs")

def clean_prop_type(prop_type):
  stripped_prop_type = re.sub(r"[\s]*", '', prop_type)
  stripped_prop_type = re.sub(r'React\.PropTypes\.', '', stripped_prop_type)

  if "oneOfType" in stripped_prop_type:
    return stripped_prop_type
  elif "instanceOf" in stripped_prop_type:
    return stripped_prop_type
  elif "oneOf" in stripped_prop_type:
    return stripped_prop_type
  elif "arrayOf" in stripped_prop_type:
    return stripped_prop_type
  elif "shape" in stripped_prop_type:
    return stripped_prop_type
  else:
    return stripped_prop_type.capitalize()

def get_file_info(file):
  component_info = {
    "display_name": "UntitledComponent",
    "props": []
  }

  is_getting_prop_types = False

  current_prop = None

  for line in file:
    # line contains displayName:

    if "createClass" in line:
      if "module.exports = React.createClass" in line:
        continue
      elif "module.exports" in line:
        match_variable_name = re.match('^(.*)module\.exports[\s]*\=[\s]*(.*?)[\s]*\=[\s]*React\.createClass(.*)$', line)
        if match_variable_name:
          component_info["display_name"] = re.sub(r'\s', '', match_variable_name.group(2))

      else:
        match_variable_name = re.match('^[\s]*(var)?(.*?)\= React\.createClass(.*)$', line)
        if match_variable_name:
          component_info["display_name"] = re.sub(r'\s', '', match_variable_name.group(2))

    if "displayName" in line:
      match_display_name = re.match('^[\s]*displayName\:[\s]*[\"\'](.*)[\"\'](.*)\n$', line)
      if match_display_name:
        component_info["display_name"] = re.sub(r'\s', '', match_display_name.group(1))


    # line contains propTypes
    if "propTypes:" in line:
      is_getting_prop_types = True
      continue

    if is_getting_prop_types:
      stripped_line = line.rstrip('\n')
      if stripped_line.endswith("[") or stripped_line.endswith("("):
        # the line ends with ( or [
        prop_match = re.match("^[\s]*([a-zA-Z]*?)\:[\s]*(.*?)[\(\[]{0,2}$", stripped_line)
        if prop_match:
          current_prop = {
            "name": prop_match.group(1),
            "type": clean_prop_type(prop_match.group(2)),
            "sub_types": []
          }

      elif current_prop:
        # partial prop type
        word_only_line = re.sub(r'\W', '', clean_prop_type(stripped_line))

        if word_only_line == "" or word_only_line == "isRequired":
          if word_only_line == "isRequired":
            current_prop["is_required"] = True

          current_prop["type"] += "(" + ",".join(current_prop["sub_types"]) + ")"
          del(current_prop["sub_types"])
          component_info["props"].append(current_prop)
          current_prop = None
        else:
          current_prop["sub_types"].append(clean_prop_type(stripped_line))

      else:
        # it's a one line thing
        prop_match = re.match("^[\s]*([a-zA-Z]*?)\:[\s]*(.*?)(\.isRequired)?[\,]?$", stripped_line)
        if prop_match:
          is_required = False
          if prop_match.group(3):
            is_required = True

          component_info["props"].append({
            "name": prop_match.group(1),
            "type": clean_prop_type(prop_match.group(2)),
            "is_required": is_required
          })

    # line is empty
    if is_getting_prop_types and line == "\n":
      break

  return component_info


class TestFileParsing(unittest.TestCase):

    # test jsx parsing
    def test_jsx(self):
      with open(os.path.join(STUB_PATH, "stub-jsx.jsx"), 'r') as f:
        component_info = get_file_info(f)
        self.assertEqual(component_info["display_name"], "AriaStatus")
        self.assertEqual(component_info["props"][0]["name"], "message")
        self.assertEqual(component_info["props"][0]["type"], "String")
        self.assertEqual(component_info["props"][0]["is_required"], False)

    def test_jsx_two(self):
      with open(os.path.join(STUB_PATH, "stub-jsx2.jsx"), 'r') as f:
        component_info = get_file_info(f)
        self.assertEqual(component_info["display_name"], "CheckboxGroup")
        self.assertEqual(component_info["props"][0]["name"], "name")
        self.assertEqual(component_info["props"][0]["type"], "String")
        self.assertEqual(component_info["props"][0]["is_required"], True)
        self.assertEqual(component_info["props"][1]["name"], "options")
        self.assertEqual(component_info["props"][1]["type"], "Array")
        self.assertEqual(component_info["props"][1]["is_required"], True)

    def test_js(self):
      with open(os.path.join(STUB_PATH, "stub-js.js"), 'r') as f:
        component_info = get_file_info(f)
        self.assertEqual(component_info["display_name"], "InputField")
        self.assertEqual(component_info["props"][0]["name"], "value")
        self.assertEqual(component_info["props"][0]["type"], "String")
        self.assertEqual(component_info["props"][0]["is_required"], False)
        self.assertEqual(component_info["props"][1]["name"], "onChange")
        self.assertEqual(component_info["props"][1]["type"], "Func")
        self.assertEqual(component_info["props"][1]["is_required"], False)

    # display_name_with_double_quotes
    # display_name_with_single_quotes
    # display_name_with_comma
    # var_name_to_display_name
    # const_name_to_display_name
    # let_name_to_displayName
    # exports_name_createClass

    # stops_getting_prop_types_on_new_line
    # stops_getting_prop_types_on_different_key

    # parses camelCaseProp
    # parses snake_case_prop

    def test_cjsx(self):
      with open(os.path.join(STUB_PATH, "stub-cjsx.cjsx"), 'r') as f:
        component_info = get_file_info(f)
        self.assertEqual(component_info["display_name"], "NavActivityFeedToggle")

        self.assertEqual(component_info["props"][0]["name"], "isOpen")
        self.assertEqual(component_info["props"][0]["type"], "Bool")
        self.assertEqual(component_info["props"][0]["is_required"], False)

        self.assertEqual(component_info["props"][1]["name"], "lastOpenedAt")
        self.assertEqual(component_info["props"][1]["type"], "Number")
        self.assertEqual(component_info["props"][1]["is_required"], True)

        self.assertEqual(component_info["props"][2]["name"], "lastClosedAt")
        self.assertEqual(component_info["props"][2]["type"], "Number")
        self.assertEqual(component_info["props"][2]["is_required"], False)

        self.assertEqual(component_info["props"][3]["name"], "hasNewNotifications")
        self.assertEqual(component_info["props"][3]["type"], "Bool")
        self.assertEqual(component_info["props"][3]["is_required"], True)

        self.assertEqual(component_info["props"][4]["name"], "showPipe")
        self.assertEqual(component_info["props"][4]["type"], "Bool")
        self.assertEqual(component_info["props"][4]["is_required"], False)

    def test_cjsx2(self):
      with open(os.path.join(STUB_PATH, "stub-cjsx2.cjsx"), 'r') as f:
        component_info = get_file_info(f)
        self.assertEqual(component_info["display_name"], "NavActivityFeedToggle")

    def test_cjsx3(self):
      with open(os.path.join(STUB_PATH, "stub-cjsx3.cjsx"), 'r') as f:
        component_info = get_file_info(f)
        self.assertEqual(component_info["display_name"], "NavActivityFeedToggle")


# if __name__ == '__main__' and __package__ is None:
#   from os import sys, path
#   sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

if __name__ == '__main__':
  unittest.main()