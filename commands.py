import sublime, sublime_plugin
import os

from ReactComponentAutocomplete.parsing import *


class AddRequireCommand(sublime_plugin.TextCommand):
  def run(self, edit, component):
    check_pattern = u"{} \= require".format(component["display_name"])
    syntax = get_syntax(self.view.settings().get('syntax'))

    if not self.view.find(check_pattern, 0):
      relative_path = os.path.relpath(component["path"], os.path.dirname(self.view.file_name()))
      relative_path = os.path.splitext(relative_path)[0]

      if syntax == "CJSX":
        require_text = "\n{} = require '{}'\n".format(component["display_name"], relative_path)
      else:
        require_text = "\n{} = require('{}');\n".format(component["display_name"], relative_path)

      all_requires = self.view.find_all("[a-zA-Z]* \= require", 0)
      if all_requires:
        insert_at = self.view.line(all_requires[-1]).end()
      else:
        insert_at = self.view.line(0).end()

      self.view.insert(edit, insert_at, require_text)
