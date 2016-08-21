import sublime, sublime_plugin

import json
import base64
import urllib
import re
 
GITHUB_SEARCH = u"{}api/v3/search/code?q=displayName%20{}+in:file+repo:{}&access_token={}"
CONTENTS_URL = u"{}api/v3/repos/{}/contents/{}?access_token={}"

MIN_WORD_SIZE = 4
MAX_WORD_SIZE = 50

class AddRequireCommand(sublime_plugin.TextCommand):
  def run(self, edit, component):
    check_pattern = u"{} \= require".format(component["displayName"])
    if self.view.find(check_pattern, 0):
      print("require already present")
    else:
      path = re.sub('\.cjsx$', '', component["path"])
      path = re.sub("src\/scripts\/", "", path)

      require_text = "\n{} = require '{}'\n".format(component["displayName"], path)
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
    self.last_added_component = None
    self.component_cache = {}

  """
  Load data from a url
  """
  def load_url(self, url):
    x = urllib.request.urlopen(url)
    raw_data = x.read()
    encoding = x.info().get_content_charset('utf8')  # JSON default
    data = json.loads(raw_data.decode(encoding))
    return data

  """
  Find available propTypes for specified file
  """
  def find_props(self, contents):
    # first find the line with propTypes
    findPropTypes = re.search(re.compile('^[\s]{2}propTypes\:$', re.MULTILINE), contents)
    if findPropTypes:
      start = findPropTypes.start()
    else:
      print("Couldn't find start, exiting")
      return []
    
    # strip the contents before the line (we don't need them)
    leftStrippedContents = contents[start:]

    # find the first empty line
    findEmptyLines = re.search(re.compile('^$', re.MULTILINE), leftStrippedContents)
    if findEmptyLines:
      end = findEmptyLines.start()
    else:
      print("Couldn't find end, exiting")
      return []

    # strip everything after it
    propTypeString = leftStrippedContents[:end]

    # and loop through the string to build a list of available props
    pattern = re.compile("^[\s]{4}([a-z]*?)\: (.*?)(\.isRequired)?$", re.MULTILINE)
    result = []
    for (propName, propType, required) in re.findall(pattern, propTypeString):
      isRequired = False
      if required:
        isRequired = True

      result.append({ "name": propName, "type": propType, "required": isRequired })

    return result

  """
  Finds component's displayName
  """
  def find_display_name(self, contents):
    matchDisplayName = re.search(re.compile('^[\s]{2}displayName\: [\"\'](.*)[\"\']$', re.MULTILINE), contents)
    if matchDisplayName:
      return matchDisplayName.group(1)
    else:
      return ""


  def find_current_file_last_require(self, view):
    print("FOUND YA")

  """
  Runs?
  """
  def on_query_context(self, view, key, operator, operand, match_all):
    # print("ON QUERY CONTEXT", key, operator, operand, match_all)
    # if key is "panel" and operator is "incremental_find":
    component_name = view.substr(view.word(view.sel()[0].begin()-2))
    self.last_added_component = component_name

    view.run_command("add_require", {"component": self.component_cache[self.last_added_component]})

  """
  Runs when user starts typing
  """
  def on_query_completions(self, view, prefix, locations):
    access_token = view.settings().get("ReactAutocomplete")["access_token"]
    github_repo = view.settings().get("ReactAutocomplete")["github_repo"]
    github_url = view.settings().get("ReactAutocomplete")["github_url"]

    # Ignore anything shorter or longer than bounds
    if len(prefix) < MIN_WORD_SIZE or len(prefix) > MAX_WORD_SIZE:
      return []

    # Ignore anything that's not JSX
    if view.match_selector(locations[0], "jsx.tag-area.coffee"):
      cursor_start = locations[0] - len(prefix) - 1
      is_start_of_component = view.substr(sublime.Region(cursor_start, cursor_start + 1)) == "<"

      if is_start_of_component:
        # we're adding a new component here
        # on select, it should
        # * add the require statement
        # * add and wrap the component
        # * add all props marked as `isRequired`
        print(prefix)
        search_results = self.load_url(GITHUB_SEARCH.format(github_url, prefix, github_repo, access_token))
        print(search_results["total_count"])
        if search_results["total_count"] > 0:
          # item = search_results["items"][0]
          # print(displayName, props)

          # if displayName and props
          # return [("{} \t {}".format(item["name"], item["path"]), item["name"]) for item in search_results["items"]]
          components = []
          
          # only take top 5 components
          for item in search_results["items"][:5]:
            file = self.load_url(CONTENTS_URL.format(github_url, github_repo, item["path"], access_token))
            file_content = base64.b64decode(file['content']).decode('utf-8')
            props = self.find_props(file_content)
            displayName = self.find_display_name(file_content)
            
            propString = ""
            for prop in props:
              # if prop["required"]:
              propString = propString + "  " + prop["name"] + "={###" + prop["type"] + "###}\n"

            suggestion = {
              "title": "{} \t {}".format(item["name"], item["path"]),
              "suggestion": "" + displayName + "\n" + propString + "/>"
            }
            self.component_cache[displayName] = {
              "suggestion": suggestion,
              "props": props,
              "displayName": displayName,
              "path": item["path"]
            }
            components.append(suggestion)

          return [(component["title"], component["suggestion"]) for component in components]
        else:
          print("no items found")
          return []


      else:
        # we want to get list of available props
        # file = self.load_url(CONTENTS_URL.format(items["GuideDashboard"], ACCESS_TOKEN))
        # props = self.find_props(base64.b64decode(file['content']).decode('utf-8'))
        # sugs = [("{} \t {} \t {}".format(prop["name"], prop["type"], prop["required"]), "{}=''".format(prop["name"]) ) for prop in props]
        # return sugs
        return []

    else:
      return []

    return []