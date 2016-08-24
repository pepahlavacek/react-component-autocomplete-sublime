# Renders an activity feed toggle in navigation

NavActions = require 'actions/nav-actions'
AppConstants = require 'constants/app-constants'
moment = require 'moment-timezone'

LocalSettingsActions = require 'actions/local-settings-actions'
LocalSettingsStore = require 'stores/local-settings-store'

transitionToCurrentRoute = require 'utils/transition-to-current-route'

module.exports = React.createClass
  displayName: "Nav ActivityFeed Toggle"

  contextTypes:
    location: React.PropTypes.object
    history: React.PropTypes.object
    params: React.PropTypes.object
    router: React.PropTypes.object
    routes: React.PropTypes.array

  propTypes:
    isOpen: React.PropTypes.bool
    lastOpenedAt: React.PropTypes.number.isRequired
    lastClosedAt: React.PropTypes.number
    hasNewNotifications: React.PropTypes.bool.isRequired,
    showPipe: React.PropTypes.bool

  getDefaultProps: ->
    isOpen: false
    lastOpenedAt: null
    lastClosedAt: null

  render: ->
    <div />