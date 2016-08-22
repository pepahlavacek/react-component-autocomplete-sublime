# Sublime Text React Component Autocomplete
Work in progress.

## Overview
This sublime package autocompletes react components.
When you start typing `<ComponentName...` it searches a specified folder in the project and suggests existing components with their props.
Once you select a component, it also automatically appends a `require` statement after last existing require, or at the top of the file.

## Limitations
Right now it only works for `cjsx` components in a very specific format.

## Installation
Clone this repo into `~/Library/Application\ Support/Sublime\ Text\ 3/Packages/ReactAutocomplete/`

[Generate an access token](https://github.com/settings/tokens)

Add file named `.react-autocomplete` to your project's root folder.
The only contents of the file should be a path the component folder of the project (folder with components you'd like to autocomplete).

For example:
```
src/scripts/components
```
