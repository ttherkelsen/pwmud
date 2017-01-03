/*
 * Core is the ancestor of all objects.  It defines various core
 * methods that all objects need.
 */

Lowtek.Core = function(opts) {
    var me = this;
    
    for (var p in opts) {
	if (p.substr(0, 1) === '_' || !opts.hasOwnProperty(p) || !(p in me)) continue;
	if (typeof me[p] === 'function' || typeof opts[p] === 'function') continue;
	
	me[p] = opts[p];
    }
    me._options = opts;
};

Lowtek.Core.prototype = {
    _options: null,

    callSuper: function() { // cls, method, arg1, ..., argN
	var me = this;
	
	var cls = arguments[0];
	var method = arguments[1];
	var args = Array.prototype.slice.call(arguments, 2);

	return cls.prototype[method].apply(me, args);
    },
    
    debug: function() {
	Lowtek.debug.apply(null, arguments);
    },
};
