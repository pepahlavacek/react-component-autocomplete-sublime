
var CheckboxGroup = React.createClass({

    mixins: [Formsy.Mixin, ComponentMixin],
    displayName: 'ComponentName'
    propTypes: {
        name: React.PropTypes.string.isRequired,
        options: React.PropTypes.array.isRequired
    },
