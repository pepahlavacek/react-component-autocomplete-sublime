import sublime, sublime_plugin

import json
import base64
import urllib
import re
import os

MIN_WORD_SIZE = 4
MAX_WORD_SIZE = 50

class AddRequireCommand(sublime_plugin.TextCommand):
  def run(self, edit, component):
    check_pattern = u"{} \= require".format(component["display_name"])
    if self.view.find(check_pattern, 0):
      # require is already present, we're done here
      print("eh")
    else:
      path = re.sub('\.cjsx$', '', component["path"])
      path = re.sub(".*?src\/scripts\/", "", path)

      require_text = "\n{} = require '{}'\n".format(component["display_name"], path)
      all_requires = self.view.find_all("[a-zA-Z]* \= require", 0)
      if all_requires:
        insert_at = self.view.line(all_requires[-1]).end()
      else:
        insert_at = self.view.line(0).end()

      self.view.insert(edit, insert_at, require_text)

class ReactAutocomplete(sublime_plugin.EventListener):
  """
  Provide component name completions for Builder
  """
  def __init__(self):
    self.components = {}
    self.component_names = []
    self.component_name_suggestions = []
    self.initial_autocomplete_point = None

  def on_load(self, view):
    self.preload_files(view)

  def find_settings_file(self, view):
    folders = os.path.dirname(view.file_name()).split("/")
    settings_path = None
    for folder in reversed(folders):
      path = '/'.join(folders)
      is_file = os.path.isfile(os.path.join(path,".react-autocomplete"))
      if is_file:
        settings_path = os.path.join(path,".react-autocomplete")
        break
      del folders[-1]

    return settings_path

  def get_component_folder(self, settings_file):
    with open(settings_file, 'r', encoding="utf-8") as f:
      settings_file_contents = f.read()
      component_folder = os.path.join(os.path.dirname(settings_file), settings_file_contents)

      return component_folder

  def clean_prop_type(self, prop_type):
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

  def get_file_info(self, file):
    component_info = {
      "display_name": "Untitled Component",
      "props": []
    }

    is_getting_prop_types = False

    current_prop = None

    for line in file:
      # line contains displayName:
      if "displayName" in line:
        match_display_name = re.match('^[\s]{2}displayName\: [\"\'](.*)[\"\']\n$', line)
        if match_display_name:
          component_info["display_name"] = match_display_name.group(1)
        else:
          component_info["display_name"] = "Untitled Component"
          continue


      # line contains propTypes
      if "propTypes:" in line:
        is_getting_prop_types = True
        continue

      if is_getting_prop_types:
        stripped_line = line.rstrip('\n')
        if stripped_line.endswith("[") or stripped_line.endswith("("):
          # the line ends with ( or [
          prop_match = re.match("^[\s]{4}([a-z]*?)\: (.*?)[\(\[]{0,2}$", stripped_line)
          if prop_match:
            current_prop = {
              "name": prop_match.group(1),
              "type": self.clean_prop_type(prop_match.group(2)),
              "sub_types": []
            }

        elif current_prop:
          # partial prop type
          word_only_line = re.sub(r'\W', '', self.clean_prop_type(stripped_line))

          if word_only_line == "" or word_only_line == "isRequired":
            if word_only_line == "isRequired":
              current_prop["is_required"] = True

            current_prop["type"] += "(" + ",".join(current_prop["sub_types"]) + ")"
            del(current_prop["sub_types"])
            component_info["props"].append(current_prop)
            current_prop = None
          else:
            current_prop["sub_types"].append(self.clean_prop_type(stripped_line))

        else:
          # it's a one line thing
          prop_match = re.match("^[\s]{4}([a-z]*?)\: (.*?)(\.isRequired)?$", stripped_line)
          if prop_match:
            is_required = False
            if prop_match.group(3):
              is_required = True

            component_info["props"].append({
              "name": prop_match.group(1),
              "type": self.clean_prop_type(prop_match.group(2)),
              "is_required": is_required
            })

      # line is empty
      if is_getting_prop_types and line == "\n":
        break

    return component_info
      # we're done here

  def preload_files(self, view):
    self.components = {}
    self.component_names = []
    self.component_name_suggestions = []

    settings_file = self.find_settings_file(view)

    if settings_file:
      component_folder = self.get_component_folder(settings_file)
    else:
      return

    for root, dirs, files in os.walk(component_folder, topdown=False):
      for name in files:
        with open(os.path.join(root, name), 'r', encoding='utf-8') as f:
          component_info = self.get_file_info(f)

          suggestion = {
            "title": "{} \t {}".format(component_info["display_name"], name),
            "suggestion": "" + component_info["display_name"] + "\n" + self.get_prop_string(component_info["props"]) + "/>"
          }

          self.components[component_info["display_name"]] = {
            "suggestion": suggestion,
            "props": component_info["props"],
            "display_name": component_info["display_name"],
            "path": os.path.join(root, name)
          }

          self.component_names.append(component_info["display_name"])
          self.component_names.sort()

    self.component_name_suggestions = [(self.components[name]["suggestion"]["title"], self.components[name]["suggestion"]["suggestion"]) for name in self.component_names]

  """
  When 
  """
  def on_modified(self, view):
    if self.initial_autocomplete_point:
      component_name = (view.substr(view.word(self.initial_autocomplete_point)))
      print(component_name)
      if component_name in self.components:
        view.run_command("add_require", {"component": self.components[component_name]})
        self.initial_autocomplete_point = None

  """
  Runs when user starts typing
  """
  def on_query_completions(self, view, prefix, locations):
    self.preload_files(view)
    self.initial_autocomplete_point = None

    if view.match_selector(locations[0], "jsx.tag-area.coffee"):
      self.initial_autocomplete_point = locations[0] - len(prefix)
      cursor_start = locations[0] - len(prefix) - 1
      is_start_of_component = view.substr(sublime.Region(cursor_start, cursor_start + 1)) == "<"

      if is_start_of_component:
        return self.component_name_suggestions
      else:
        # we want to get list of available props
        # file = self.load_url(CONTENTS_URL.format(items["GuideDashboard"], ACCESS_TOKEN))
        # props = self.find_props(base64.b64decode(file['content']).decode('utf-8'))
        # sugs = [("{} \t {} \t {}".format(prop["name"], prop["type"], prop["required"]), "{}=''".format(prop["name"]) ) for prop in props]
        # return sugs
        return []
    else:
      return []