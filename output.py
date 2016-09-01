import re

def strip_comma_from_strings(item_list):
  return [(re.sub(",", "", item)) for item in item_list]

def get_list_of_values(item_list, syntax, translate = False):
  items = []
  for item in item_list:
    # strip comma
    item = re.sub(",", "", item)
    if translate:
      item = get_translated_value(item, syntax)

    items.append(item)
  
  return items

def get_translated_value(name, syntax):
  name = re.sub("\.isRequired", "", name)

  values = {
    "JSX": {
      "object": "{}",
      "string": '""',
      "number": 'Number()',
      "bool": 'true',
      "func": "function() {}",
      "array": "[]",
      "symbol": "Symbol()",
      "node": '"" || Number() || []',
      "element": "React.createElement(type, props, children)",
    },
    "CJSX": {
      "object": "{}",
      "string": '""',
      "number": 'Number()',
      "bool": 'true',
      "func": "(() -> )",
      "array": "[]",
      "symbol": "Symbol()",
      "node": '"" || Number() || []',
      "element": "React.createElement(type, props, children)",
    }
  }

  if name in values[syntax]:
    return values[syntax][name]
  else:
    return name

def match_one_of_style(pattern_name, translate, prop_type, sub_types, syntax):
  pattern = "^" + pattern_name + "[\(\[]{0,2}([^\)\]]*)[\)\]]{0,2}$"

  if syntax == "JSX":
    connector = " || "
  else:
    connector = " or "

  if len(sub_types) > 0:
    return connector.join(get_list_of_values(sub_types, syntax, False))
  else:
    match_options = re.match(pattern, prop_type)
    if match_options:
      sub_types = get_list_of_values(match_options.group(1).split(","), syntax, False)
      return connector.join(sub_types)
    else:
      return prop_type

def get_object_from_shape(sub_types, syntax):
  output_list = []
  for sub_type in sub_types:
    [key, value] = sub_type.split(":")
    output_list.append("{}: {}".format(key, get_translated_value(value, syntax)))

  return "{" + ", ".join(output_list) + "}"


def get_value_for_type(prop_type, sub_types, syntax):

  if "oneOfType" in prop_type:
    return match_one_of_style("oneOfType", True, prop_type, sub_types, syntax)

  elif "oneOf" in prop_type:
    return match_one_of_style("oneOf", False, prop_type, sub_types, syntax)

  elif "arrayOf" in prop_type:
    match_instance = re.match(r"^arrayOf[\( ]{0,1}([^\)]*)[\) ]{0,1}$", prop_type)
    if match_instance:
      if "shape" in match_instance.group(1):
        return get_object_from_shape(sub_types, syntax)
      else:
        return "[" + match_instance.group(1) + "]"
    else:
      return prop_type

  elif "instanceOf" in prop_type:
    match_instance = re.match(r"^instanceOf[\(]{0,2}([^\)]*)[\)]{0,2}$", prop_type)
    if match_instance:
      return "new " + match_instance.group(1) + "()"
    else:
      return prop_type

  elif "shape" in prop_type:
    return get_object_from_shape(sub_types, syntax)

  else:
    return get_translated_value(prop_type, syntax)

def get_prop_string(props, tab_size, syntax):
  prop_string = ""
  indent = " " * tab_size

  for prop in props:
    prop_string = prop_string + indent + prop["name"] + "={" + get_value_for_type(prop["type"], prop["sub_types"], syntax) + "}\n"

  return prop_string