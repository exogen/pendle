pendle = window.pendle || {};

pendle.slideIn = function(element) {
	element = $(element);
	var width = element.width();
	element.css({marginLeft: -width}).animate({marginLeft: 0}, 400);
};

pendle.slideOut = function(element) {
	element = $(element);
	var width = element.width();
	element.css({marginLeft: 0}).animate({
		paddingTop: 0,
		paddingBottom: 0,
		height: 0,
		marginLeft: -width
	}, 200, function() { $(this).remove(); });
};

pendle.Reservation = pendle.Model.registry.types['reservations:reservation'] = function(data) {
	$.extend(this, data);
	this.templates = {
		reservation: 'customer-reservation-template'
	};
};

pendle.Reservation.prototype = new pendle.Model();

pendle.Reservation.prototype.init = function() {
	if (this.asset) {
		this.asset = pendle.Model.registry.get(this.asset);
		this.asset.reservation = this;
	}
	if (this.transaction) {
		this.transaction = pendle.Model.registry.get(this.transaction)
		if (this.transaction.customer && !(this.transaction.customer instanceof pendle.Customer)) {
			this.transaction.customer = pendle.Model.registry.get(this.transaction.customer);
		}
	}
};

pendle.Customer = pendle.Model.registry.types['auth:user'] = function(data) {
	$.extend(this, data);
	this.templates = {
		reservation: 'customer-reservation-template'
	};
	this.displayName = ko.dependentObservable(function() {
		if (this.fields.first_name || this.fields.last_name) {
			return [this.fields.first_name, this.fields.last_name].join(" ");
		}
		else {
			return this.fields.username;
		}
	}, this);
};

pendle.Customer.prototype = new pendle.Model();

pendle.Customer.prototype.toString = function() {
	return this.displayName();
};

pendle.Customer.prototype.init = function() {
	this.departments = pendle.Model.registry.getMany(this.departments);
	this.departments.toString = ko.dependentObservable(function() {
		var departments = this;
		var names = [];
		for (var i = 0; i < departments.length; i++) {
			var department = departments[i];
			names.push(department.fields.name);
		}
		return names.join(", ");
	}, this.departments);
	this.assets = {};
	if (this.reservations) {
		this.reservations = pendle.Model.registry.getMany(this.reservations);
		for (var i = 0; i < this.reservations.length; i++) {
			var reservation = this.reservations[i];
			var asset = reservation.asset;
			this.assets[asset.pk] = asset;
		}
		this.reservations.sort(function(a, b) {
			if (a.asset.fields.bundle < b.asset.fields.bundle) {
				return -1;
			}
			else if (a.asset.fields.bundle > b.asset.fields.bundle) {
				return 1;
			}
			else {
				return (a.asset.fields.bundle_order || 0) - (b.asset.fields.bundle_order || 0);
			}
		});
	}
};

pendle.Asset = pendle.Model.registry.types['assets:asset'] = function(data) {
	$.extend(this, data);
	this.templates = {
		reservation: 'asset-reservation-template'
	};
	/*
	if (this.reservation) {
		if (this.reservation.transaction.customer) {
			if (!customer) {
				customer = new pendle.Customer(this.reservation.transaction.customer);
			}
			this.reservation.transaction.customer = customer;
		}
	}
	this.title = ko.dependentObservable(function() {
		return this.product.fields.title || this.fields.barcode;
	}, this);
	this.manufacturer = ko.dependentObservable(function() {
		return this.product.manufacturer && this.product.manufacturer.fields.name;
	}, this);
	*/
	this.box = ko.observable(null);
	this.confirmed = ko.observable(false);
	this.confirmed.subscribe(function(value) {
		pendle.transaction.asset.focused(true);
		if (value) {
			pendle.transaction.add(this);
		}
		else {
			var remove = this.box().remove; // Safety first.
			if (remove) {
				this.box(null);
				remove(this);
			}
			if (this.bundled && this.bundled.length) {
				for (var i = 0; i < this.bundled.length; i++) {
					var asset = this.bundled[i];
					if (asset.confirmed())
						asset.confirmed(false);
				}
			}
		}
	}.bind(this));
};

pendle.Asset.prototype = new pendle.Model();

pendle.Asset.prototype.init = function() {
	if (this.product) {
		this.product = pendle.Model.registry.get(this.product);
		if (this.product.manufacturer)
			this.product.manufacturer = pendle.Model.registry.get(this.product.manufacturer);
	}
	this.title = ko.dependentObservable(function() {
		if (this.product && this.product.fields.title)
			return this.product.fields.title
		else
			return this.barcode
	}, this);
	this.reservation = this.reservation ?
		(this.reservation instanceof pendle.Reservation ? this.reservation :
		pendle.Model.registry.get(this.reservation)) : null;
	this.bundle = this.bundle || null;
	if (this.bundled) {
		if (!(this.bundled instanceof Array)) {
			this.bundled = pendle.Model.registry.getMany(this.bundled);
			for (var i = 0; i < this.bundled.length; i++) {
				this.bundled[i].bundle = this;
			}
		}
	}
	else {
		this.bundled = null;
		this.customerBundled = null;
	}
	this.bundleSynced = function() {
		if (this.bundle) {
			if (!this.reservation != !this.bundle.reservation)
				return false;
			if (this.reservation) {
				if (this.reservation.transaction.customer != this.bundle.reservation.transaction.customer)
					return false;
			}
		}
		return true;
	}.bind(this);
};

pendle.Asset.prototype.toString = function() {
	return this.fields.barcode;
};

pendle.Scanner = function(config) {
	this.templates = {
		message: 'message-template'
	};
	this.message = ko.observable();
	this.result = ko.observable();
	this.focused = ko.observable(false);
	this.loading = ko.observable(false);
	this.stale = ko.observable(false);
	this.query = ko.observable("");
	this.query.subscribe(function(value) {
		this.stale(true);
	}.bind(this));
};

pendle.Scanner.prototype = new pendle.Model();

pendle.Scanner.prototype.init = function(element) {
	this.element = $(element);
	this.form = this.element.find('form:first');
	this.messageElement = this.element.find('div.message:first');
	this.message.subscribe(function(value) {
		if (value) {
			ko.applyBindings(this, value[0]);
			this.messageElement.empty().append(value);
		}
	}.bind(this));
	ko.applyBindings(this, this.element[0]);
}

pendle.Scanner.prototype.add = function(form) {
	form = $(form);
	var data = form.serialize();
	$.ajax({
		beforeSend: function(request) {
			this.loading(true);
		},
		cache: false,
		context: this,
		data: data,
		dataType: 'json',
		complete: function(request, status) {
			this.loading(false);
		},
		error: function(request, status) {
			this.result(null);
			this.focused(true);
			var data = $.parseJSON(request.responseText);
			if (data.message)
				this.message($(data.message));
		},
		success: function(data, status, request) {
			this.message(null);
			if (data.objects) {
				pendle.Model.registry.registerMany(data.objects)
			}
			if (data.result) {
				var result = pendle.Model.registry.get(data.result);
				this.result(result);
			}
			this.stale(false);
		},
		timeout: 30000,
		type: 'POST',
		url: form.attr('action')
	});
};

pendle.Scanner.prototype.load = function(form) {
	if (this.query()) {
		var data = this.form.serialize();
		$.ajax({
			beforeSend: function(request) {
				this.loading(true);
			},
			cache: false,
			context: this,
			data: data,
			dataType: 'json',
			complete: function(request, status) {
				this.loading(false);
			},
			error: function(request, status) {
				this.result(null);
				this.focused(true);
				var data = $.parseJSON(request.responseText);
				if (data.message)
					this.message($(data.message));
			},
			success: function(data, status, request) {
				this.message(null);
				if (data.objects) {
					pendle.Model.registry.registerMany(data.objects)
				}
				if (data.result) {
					var result = pendle.Model.registry.get(data.result);
					this.result(result);
				}
				this.stale(false);
			},
			timeout: 30000,
			type: 'GET',
			url: this.form.attr('action')
		});
	}
	else {
		this.result(null);
	}
};

pendle.Transaction = function(customer, asset) {
	this.templates = {
		asset: 'transaction-asset-template'
	}
	this.customer = customer;
	this.customer.result.subscribe(function(value) {
		if (value) {
			this.asset.focused(true);
		}
		else {
			this.customer.focused(true);
		}
	}.bind(this));
	this.asset = asset;
	this.asset.result.subscribe(function(asset) {
		if (asset) {
			if (asset.bundle) {
				if (asset.bundleSynced() || !asset.bundle.confirmed())
					asset.confirmed(true); // This will focus the asset scanner.
			}
			else {
				asset.confirmed(true); // This will focus the asset scanner.
			}
		}
		else {
			this.asset.focused(true);
		}
	}.bind(this));
	this.inbox = ko.observableArray([]);
	this.inbox.subscribe(function(value) {
		for (var i = 0; i < value.length; i++) {
			value[i].box(this);
		}
	}.bind(this.inbox));
	this.outbox = ko.observableArray([]);
	this.outbox.subscribe(function(value) {
		for (var i = 0; i < value.length; i++) {
			value[i].box(this);
		}
	}.bind(this.outbox));
	this.customerID = ko.dependentObservable(function() {
		var customer = this.customer.result();
		return customer ? customer.pk : null;
	}, this);
	this.assetCount = ko.dependentObservable(function() {
		return this.inbox().length + this.outbox().length;
	}, this);
	this.ready = ko.dependentObservable(function() {
		return this.customer.result() && this.assetCount() > 0;
	}, this);
};

pendle.Transaction.prototype = new pendle.Model();

pendle.Transaction.prototype.init = function(element) {
	this.element = $(element);
	ko.applyBindings(this, this.element[0]);
};

pendle.Transaction.prototype.add = function(asset) {
	if (asset.box()) {
		// Already in a box!
	}
	else {
		var box = asset.available ? this.outbox : this.inbox;
		box.push(asset);
	}
};

jQuery(function($) {
	pendle.customer = new pendle.Scanner();
	pendle.customer.templates.result = 'customer-result-template';
	pendle.customer.init('#scan-customer');

	pendle.asset = new pendle.Scanner();
	pendle.asset.templates.result = 'asset-result-template';
	pendle.asset.init('#scan-asset');

	pendle.transaction = new pendle.Transaction(pendle.customer, pendle.asset);
	pendle.transaction.init('#transaction');

	pendle.customer.focused(true);
});
