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
        break;
      del folders[-1]

    return settings_path

  def get_component_folder(self, settings_file):
    with open(settings_file, 'r', encoding="utf-8") as f:
      settings_file_contents = f.read()
      component_folder = os.path.join(os.path.dirname(settings_file), settings_file_contents)

      return component_folder

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
          file_content = f.read() 
          display_name = self.find_display_name(file_content)
          props = self.find_props(file_content)

          suggestion = {
            "title": "{} \t {}".format(display_name, name),
            "suggestion": "" + display_name + "\n" + self.get_prop_string(props) + "/>"
          }

          self.components[display_name] = {
            "suggestion": suggestion,
            "props": props,
            "display_name": display_name,
            "path": os.path.join(root, name)
          }

          self.component_names.append(display_name)
          self.component_names.sort()

    self.component_name_suggestions = [(self.components[name]["suggestion"]["title"], self.components[name]["suggestion"]["suggestion"]) for name in self.component_names]

  """
  Find available propTypes for specified file
  """
  def find_props(self, contents):
    # first find the line with propTypes
    findPropTypes = re.search(re.compile('^[\s]{2}propTypes\:$', re.MULTILINE), contents)
    if findPropTypes:
      start = findPropTypes.start()
    else:
      # print("Couldn't find start, exiting")
      return []
    
    # strip the contents before the line (we don't need them)
    left_stripped_contents = contents[start:]

    # find the first empty line
    find_empty_lines = re.search(re.compile('^$', re.MULTILINE), left_stripped_contents)
    if find_empty_lines:
      end = find_empty_lines.start()
    else:
      # print("Couldn't find end, exiting")
      return []

    # strip everything after it
    prop_type_string = left_stripped_contents[:end]

    # and loop through the string to build a list of available props
    pattern = re.compile("^[\s]{4}([a-z]*?)\: (.*?)(\.isRequired)?$", re.MULTILINE)
    result = []
    for (prop_name, prop_type, required) in re.findall(pattern, prop_type_string):
      isRequired = False
      if required:
        isRequired = True

      result.append({ "name": prop_name, "type": prop_type, "required": isRequired })

    return result

  """
  Finds component's displayName
  """
  def find_display_name(self, contents):
    match_display_name = re.search(re.compile('^[\s]{2}displayName\: [\"\'](.*)[\"\']$', re.MULTILINE), contents)
    if match_display_name:
      return match_display_name.group(1)
    else:
      return ""

  def get_prop_string(self, props):
    prop_string = ""
    for prop in props:
      # if prop["required"]:
      prop_string = prop_string + "  " + prop["name"] + "={###" + prop["type"] + "###}\n"
    return prop_string

  """
  Runs?
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