import re
import os

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
        match_variable_name = re.match('^[\s]*(var|const|let)?(.*?)\= React\.createClass(.*)$', line)
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
        # it's probably a multiline prop definition (arrayOf, oneOf, oneOfType, something like that)
        prop_match = re.match("^[\s]*([a-zA-Z_]*?)\:[\s]*(.*?)[\(\[]{0,2}$", stripped_line)
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
        prop_match = re.match("^[\s]*([a-zA-Z_]*?)\:[\s]*(.+?)(\.isRequired)?[\,]?$", stripped_line)
        if prop_match:
          is_required = False
          if prop_match.group(3):
            is_required = True

          component_info["props"].append({
            "name": prop_match.group(1),
            "type": clean_prop_type(prop_match.group(2)),
            "is_required": is_required
          })
        else:
          is_getting_prop_types = False
          break

    # line is empty
    if is_getting_prop_types and line == "\n":
      is_getting_prop_types = False
      break

    # line is a closing curly bracket
    if is_getting_prop_types and "}" in line:
      is_getting_prop_types = False
      break

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
