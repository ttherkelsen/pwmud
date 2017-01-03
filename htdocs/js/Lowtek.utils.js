Lowtek = {};
Lowtek.util = {};

Lowtek.DEBUG = true;
Lowtek.GUID = 1;

Lowtek.debug = function() {
    if (Lowtek.DEBUG) {
	console.log.apply(null, arguments);
    }
};

Lowtek.nextGUID = function() {
    return Lowtek.GUID++;
};

Lowtek.util.ns = function() {
    for (var i = 0; i < arguments.length; i++) {
	var parts = arguments[i].split(".");
	var obj = window;

	for (var j = 0; j < parts.length; j++) {
	    if (!(parts[j] in obj)) {
		obj[parts[j]] = {};
	    }
	    obj = obj[parts[j]];
	};
    }
};

Lowtek.util.merge = function(/* obj1, ..., objN */) {
    var obj1 = arguments[0];

    for (var i = 1; i < arguments.length; i++) {
	var objN = arguments[i];

	for (var p in objN) {
	    if (objN.hasOwnProperty(p)) {
		obj1[p] = objN[p];
	    }
	}
    }

    return obj1;
};

// Only difference between merge and mixin is that the latter will not
// overwrite existing properties in obj1
Lowtek.util.mixin = function(/* obj1, ..., objN */) {
    var obj1 = arguments[0];

    for (var i = 1; i < arguments.length; i++) {
	var objN = arguments[i];

	for (var p in objN) {
	    if (objN.hasOwnProperty(p) && !(p in obj1)) {
		obj1[p] = objN[p];
	    }
	}
    }

    return obj1;
};

Lowtek.util.inherit = function(subClass, superClass) {
    subClass.prototype = Object.create(superClass.prototype);
    subClass.prototype.constructor = subClass;
};

Lowtek.util.objectSize = function(obj) {
    var size = 0;

    for (var k in obj) {
	if (obj.hasOwnProperty(k)) {
	    size++;
	}
    }

    return size;
};
