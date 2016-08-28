
def get_value_for_type(prop_type, syntax):
  values = {
    "JSX": {
      "object": "{}",
      "string": '""',
      "number": 'Number()',
      "bool": 'true',
      "function": "function() {}",
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
      "function": "(() -> )",
      "array": "[]",
      "symbol": "Symbol()",
      "node": '"" || Number() || []',
      "element": "React.createElement(type, props, children)",
    }
  }

  return values[syntax][prop_type]

def get_prop_string(props, tab_size, syntax):
  prop_string = ""
  indent = " " * tab_size

  for prop in props:
    prop_string = prop_string + indent + prop["name"] + "={" + get_value_for_type(prop["type"], syntax) + "}\n"

  return prop_string