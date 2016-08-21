# (Very much work in progress, don't download it yet)
# Sublime Text React Component Autocomplete

## Overview
This sublime package autocompletes react components from a selected repository.
When you start typing `<ComponentName...` it searches a preselected repo and suggests existing components with their props.
Once you select a component, it also automatically appends a `require` statement for it.

## Limitations
Right now it only works for `cjsx` components in a very specific format.

## Installation
Clone this repo into `~/Library/Application\ Support/Sublime\ Text\ 3/Packages/ReactAutocomplete/`

[Generate an access token](https://github.com/settings/tokens)

In Sublime Text 3, go to `Sublime Text > Preferences > Settings - User` and add the following settings:
```
{
  "ReactAutocomplete": {
  	"access_token": "[paste your access token here]"
    "github_repo": "https://github.com/[your repo]"
  }
}
```
