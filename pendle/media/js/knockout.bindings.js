ko.bindingHandlers.focused = {
	init: function(element, value) {
		$(element).mouseup(function() {
			$(this).select();
		});
	},
	update: function(element, value) {
		value = ko.utils.unwrapObservable(value());
		if (value) {
			$(element).select();
		}
		else
			element.blur();
	}
};

ko.bindingHandlers.tooltip = {
	update: function(element, value) {
		value = ko.utils.unwrapObservable(value());
		$(element).attr('title', value);
	}
};
