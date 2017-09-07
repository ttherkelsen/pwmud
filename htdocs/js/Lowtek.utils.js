"use strict";

// Ideally, one would use const here instead of var.  The problem is
// that const and let both create bindings in a special global context
// that you can't access programmatically (which ns() needs in order
// to work).  Thus this has to use var for now.  Later, once modules
// are properly supported in browsers, this will be handled with a
// module imported Singleton object instead.
var Lowtek = {};

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

Lowtek.util.objectEntries = function(obj) {
    let iter = Reflect.ownKeys(obj)[Symbol.iterator]();

    return {
        [Symbol.iterator]() {
            return this;
        },
        next() {
            let { done, value: key } = iter.next();
            if (done) {
                return { done: true };
            }
            return { value: [key, obj[key]] };
        }
    };
};

Lowtek.util.ns = function() {
    for (let i = 0; i < arguments.length; i++) {
	let obj = window;

	for (let part of arguments[i].split(".")) {
	    if (!(part in obj)) {
		obj[part] = {};
	    }
	    obj = obj[part];
	}
    }
};

Lowtek.util.merge = function(/* obj1, ..., objN */) {
    // FIXME: Is this used anymore?  Can be replaced with Object.assign()
    let obj1 = arguments[0];

    for (let i = 1; i < arguments.length; i++) {
	let objN = arguments[i];

	for (let [p, v] of Lowtek.util.objectEntries(objN)) {
	    obj1[p] = v;
	}
    }

    return obj1;
};

// Only difference between merge and mixin is that the latter will not
// overwrite existing properties in obj1
Lowtek.util.mixin = function(/* obj1, ..., objN */) {
    let obj1 = arguments[0];

    for (let i = 1; i < arguments.length; i++) {
	let objN = arguments[i];

	for (let [p, v] of Lowtek.util.objectEntries(objN)) {
	    if (!(p in obj1)) {
		obj1[p] = v;
	    }
	}
    }

    return obj1;
};

Lowtek.util.inherit = function(subClass, superClass) {
    // FIXME: This should not be used anymore
    subClass.prototype = Object.create(superClass.prototype);
    subClass.prototype.constructor = subClass;
};

Lowtek.util.objectSize = function(obj) {
    let size = 0;

    for (let [k, v] of Lowtek.util.objectEntries(obj)) {
	size++;
    }

    return size;
};
