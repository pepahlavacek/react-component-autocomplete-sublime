# Sublime Text React Component Autocomplete
Work in progress.

## Overview
This sublime package autocompletes your react components.
When you start typing `<ComponentName...` it searches a specified folder in the project and suggests existing components with their props.
Once you select a component, it also automatically appends a `require` statement after last existing require, or at the top of the file.

## Limitations
Right now it only works for `cjsx` components.

## Installation

Clone this repo in your `Packages` folder:
`git clone git@github.com:pepahlavacek/sublime-react-component-autocomplete.git ~/Library/Application\ Support/Sublime\ Text\ 3/Packages/ReactAutocomplete/`

Add file named `.react-autocomplete` to your project's root folder.
```
# .react-autocomplete
src/scripts/components
```

It should only contain a path to the component folder (folder containing components you'd like to autocomplete).

## To Do
- [ ] Use relative path in `require` statements
- [ ] Replace any file extension in `require` statements, not just `cjsx`
- [x] Parse jsx and js components
- [ ] Allow specifying file (output) format in settings file
- [ ] Clean up and deduplicate tests, make imports work there
- [ ] Take indentation settings in consideration (2 vs 4 spaces)