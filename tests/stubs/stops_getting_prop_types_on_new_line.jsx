// from https://github.com/ezequiel/react-typeahead-component/blob/master/src/components/aria_status.jsx
'use strict';

var React = require('react');

module.exports = React.createClass({
    displayName: 'Aria Status',

    propTypes: process.env.NODE_ENV === 'production' ? {} : {
        oneProp: React.PropTypes.string,
        twoProps: React.PropTypes.string,
    },

    threeProps: React.PropTypes.string,

    componentDidMount: function() {
        var _this = this;

        // This is needed as `componentDidUpdate`
        // does not fire on the initial render.
        _this.setTextContent(_this.props.message);
    },

    componentDidUpdate: function() {
