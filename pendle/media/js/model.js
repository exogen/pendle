pendle = window.pendle || {};

pendle.Model = function(data) {
	if (arguments.length > 0) {
		$.extend(this, data);
	}
};

pendle.Model.prototype.init = function() {
};

pendle.Registry = function(objects, types) {
	this.objects = objects || {};
	this.types = types || {};
};

pendle.Registry.prototype.get = function(type, id) {
	if (arguments.length == 1) {
		var reference = type;
		type = reference.type;
		if (typeof reference.id == 'undefined') {
			if (reference.ids) {
				return this.getMany(type, reference.ids);
			}
		}
		id = reference.id;
	}
	var instances = this.objects[type] || {};
	var observable = instances[id];
	return observable || null;
};

pendle.Registry.prototype.getObservable = function(type, id) {
	if (arguments.length == 1) {
		var reference = type;
		type = reference.type;
		id = reference.id;
	}
	var instances = this.objects[type] || {};
	var observable = instances[id];
	return observable || null;
};

pendle.Registry.prototype.getObservableArray = function(type, ids) {
	if (arguments.length == 1) {
		var reference = type;
		type = reference.type;
		ids = reference.ids;
	}
	var instances = this.objects[type] || {};
	var results = [];
	for (var i = 0; i < ids.length; i++) {
		var id = ids[i];
		var observable = instances[id];
		results.push(observable || null);
	}
	return ko.observableArray(results);
};

pendle.Registry.prototype.getMany = function(type, ids) {
	if (arguments.length == 1) {
		var object = type;
		type = object.type;
		ids = object.ids;
	}
	var instances = this.objects[type] || {};
	var results = [];
	for (var i = 0; i < ids.length; i++) {
		var id = ids[i];
		var observable = instances[id];
		results.push(observable || null);
	}
	return results;
};

pendle.Registry.prototype.register = function(type, id, instance, replace) {
	replace = replace || false;
	var constructor = this.types[type] || pendle.Model;
	if (!(instance instanceof constructor))
		instance = new constructor(instance);
	var instances = this.objects[type] = this.objects[type] || {};
	var observable = instances[id];
	if (!observable || replace) {
		observable = instances[id] = instance;
		instance.init();
	}
	return observable;
};

pendle.Registry.prototype.registerMany = function(objects, replace) {
	replace = replace || false;
	var constructed = [];
	for (var type in objects) {
		var instances = objects[type];
		var constructor = this.types[type] || pendle.Model;
		var registered = this.objects[type] = this.objects[type] || {};
		for (var id in instances) {
			var instance = instances[id];
			if (!(instance instanceof constructor))
				instance = new constructor(instance);
			var observable = registered[id];
			if (!observable || replace) {
				constructed.push(instance);
				observable = registered[id] = instance;
			}
		}
	}
	for (var i = 0; i < constructed.length; i++) {
		var instance = constructed[i];
		instance.init();
	}
};

pendle.Model.registry = new pendle.Registry();
