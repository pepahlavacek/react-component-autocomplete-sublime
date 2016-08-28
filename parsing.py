import re
import os

def clean_prop_type(prop_type):
  stripped_prop_type = re.sub(r"[\s]*", '', prop_type)
  stripped_prop_type = re.sub(r'React\.PropTypes\.', '', stripped_prop_type)

  # if "oneOfType" in stripped_prop_type:
  #   return stripped_prop_type
  # elif "oneOf" in stripped_prop_type:
  #   return stripped_prop_type
  # elif "instanceOf" in stripped_prop_type:
  #   return stripped_prop_type
  # elif "oneOf" in stripped_prop_type:
  #   return stripped_prop_type
  # elif "arrayOf" in stripped_prop_type:
  #   return stripped_prop_type
  # elif "shape" in stripped_prop_type:
  #   return stripped_prop_type
  # else:
  return stripped_prop_type

def should_skip_line(line):
  skip = False

  if re.match("[\s]*\/\/.*", line):
    skip = True

  if re.match("[\s]*\#[^\#].*", line):
    skip = True

  if re.match("^[\s]*$", line):
    skip = True

  return skip

def should_get_display_name(line):
  if "createClass" in line:
    return True

  if "displayName" in line:
    return True

  return False

def get_display_name(line):
  if "createClass" in line:
    if "module.exports = React.createClass" in line:
      return "UntitledComponent"
    elif "module.exports" in line:
      match_variable_name = re.match('^(.*)module\.exports[\s]*\=[\s]*(.*?)[\s]*\=[\s]*React\.createClass(.*)$', line)
      if match_variable_name:
        return re.sub(r'\s', '', match_variable_name.group(2))

    else:
      match_variable_name = re.match('^[\s]*(var|const|let)?(.*?)\= React\.createClass(.*)$', line)
      if match_variable_name:
        return re.sub(r'\s', '', match_variable_name.group(2))

  if "displayName" in line:
    match_display_name = re.match('^[\s]*displayName\:[\s]*[\"\'](.*)[\"\'](.*)$', line)
    if match_display_name:
      return re.sub(r'\s', '', match_display_name.group(1))

  return "UntitledComponent"

def get_file_info(file):
  component_info = {
    "display_name": "UntitledComponent",
    "props": []
  }

  is_getting_prop_types = False
  is_prop_types_enclosed_in_brackets = False
  prop_types_initial_indent = 0
  current_prop = None

  for non_stripped_line in file:
    line = non_stripped_line.rstrip('\n')
    current_indent = len(line) - len(line.lstrip())

    if should_skip_line(line):
      continue

    if should_get_display_name(line):
      component_info["display_name"] = get_display_name(line)
      continue

    # line contains propTypes
    if re.match("^\s*propTypes\:.*$", line):
      is_getting_prop_types = True
      prop_types_initial_indent = len(line) - len(line.lstrip())
      continue

    if is_getting_prop_types and current_indent <= prop_types_initial_indent:

      if current_prop:
        component_info["props"].append(current_prop)
        current_prop = None

      is_getting_prop_types = False
      break

    """
        Parsing prop types in action
    """
    if not is_getting_prop_types:
      continue

    if current_indent / 2 == prop_types_initial_indent:
      if current_prop:
        component_info["props"].append(current_prop)
        current_prop = None

      # this is a prop type or a beginning of one
      # so let's get a name and type
      single_line_prop_match = re.match("^[\s]*([a-zA-Z_]*?)\:[\s]*(.+?)(\.isRequired)?[\,]?$", line)
      multiline_prop_match = re.match("^[\s]*([a-zA-Z_]*?)\:[\s]*(.+?)[\(\[\{]{1,2}$", line)
      general_prop_match = re.match("^[\s]*([a-zA-Z_]*?)\:", line)

      if multiline_prop_match:
        current_prop = {
          "name": multiline_prop_match.group(1),
          "type": clean_prop_type(multiline_prop_match.group(2)),
          "sub_types": []
        }
      elif single_line_prop_match:
        is_required = False
        if single_line_prop_match.group(3):
          is_required = True

        current_prop = {
          "name": single_line_prop_match.group(1),
          "type": clean_prop_type(single_line_prop_match.group(2)),
          "is_required": is_required
        }
      elif general_prop_match:
        current_prop = {
          "name": general_prop_match.group(1),
          "type": "custom",
          "is_required": False
        }

    elif current_indent / 2 > prop_types_initial_indent:
      # this is inside of a prop type
      word_only_line = re.sub(r'\W', '', clean_prop_type(line))

      if word_only_line == "isRequired":
        current_prop["is_required"] = True
      
      if current_prop and "sub_types" in current_prop:
        current_prop["sub_types"].append(clean_prop_type(line))

    else:
      if current_prop:
        component_info["props"].append(current_prop)
        current_prop = None
    # else:
    #   print("else", line)
    # current_prop["type"] += "(" + ",".join(current_prop["sub_types"]) + ")"
    # if not current_prop and re.match("^[\s]*([a-zA-Z_]*?)\:", line):

  return component_info

def get_syntax(view_syntax):
  syntax_match = re.match(r"^(.*)\/([A-Z]*)\.tmLanguage$", view_syntax)

  syntax = "JSX"
  if syntax_match:
    syntax = syntax_match.group(2)
    if not syntax in ["JSX", "CJSX"]:
      syntax = "JSX"
  else:
    syntax = "JSX"

  return syntax