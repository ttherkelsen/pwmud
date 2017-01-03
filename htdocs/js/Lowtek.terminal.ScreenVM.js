Lowtek.util.ns('Lowtek.terminal');

Lowtek.terminal.ScreenVM = function(opts) {
    var me = this;

    Lowtek.Core.call(me, opts);
    me.init();
};

Lowtek.util.inherit(Lowtek.terminal.ScreenVM, Lowtek.Core);

Lowtek.util.merge(Lowtek.terminal.ScreenVM.prototype, {
    /* screen is a 2d array representing the characters of the screen,
     * divided into rows and columns.  Each character is always an
     * array:
     * [ (int) unicode character, (array of int arrays) colours,
     *   (object) (any other data needed, can be omitted) ]
     */
    screen: null,
    width: null,
    height: null,
    historySize: null,
    defaults: {
	glyph: 32,
	colours: [ [ 0, 0, 0, 255 ], [ 255, 255, 255, 255 ] ],
    },
    stream: null,
    funcMode: null,
    cursor: null,

    init: function() {
	var me = this;

	var screen = new Array(me.height);
	for (var i = 0; i < me.height; i++) {
	    screen[i] = new Array(me.width);
	    screen[i].fill([ me.defaults.glyph, me.defaults.colours ]);
	}
	me.screen = screen;
	me.history = [];
	me.stream = [];
	me.funcMode = false;
	me.cursor = {
	    position: { x: 0, y: 0 },
	    colours: me.defaults.colours.slice(),

	    // When the cursor is visible, a block is printed in reverse video at
	    // its position.
	    visible: true,

	    // simple - when advancing the cursor over right edge of the screen,
	    //     wrap to the next line immediately, and scroll the screen up
	    //     if necessary.
	    // overflow - upon reaching the edge, mark "overflow" and wrap just before
	    //     the next character is printed
	    // bottom - like "simple" except for the bottom row of the screen where it
	    //     is "overflow"
	    // none - never wrap, characters printed when the cursor is at the right
	    //     edge simply overwrites
	    // hidden - like "none" except the characters are not written to the screen
	    //     at all
	    wrap: 'simple',
	    wrapOverflow: false,
	}
    },

    addCharacters: function() {
	var me = this;
	Array.prototype.push.apply(me.stream, arguments);
    },

    parseStream: function() {
	var me = this;
	var stream = me.stream.join("").split("\x1b");
	me.stream = []

	for (var i = 0; i < stream.length; i++) {
	    if (me.funcMode) {
		me.parseFunctions(stream[i]);
	    }
	    else {
		me.terminal_print_chars(stream[i]);
	    }
	    me.funcMode = !me.funcMode;
	}

	if (stream[stream.length - 1]) {
	    me.funcMode = !me.funcMode;
	}
    },

    parseFunctions: function(stream) {
    },

    terminal_print_char: function(code) {
	var me = this;

	// Some stuff only happens if the cursor is at right edge before printing and overflowed
	if (me.cursor.position.x == (me.width - 1) && me.cursor.wrapOverflow) {
	    switch (me.cursor.wrap) {
	    case 'hidden':
		return; // Don't print character

	    case 'overflow':
		me.terminal_newline();
		break
	 
	    case 'bottom':
		if (me.cursor.position.y == (me.height - 1)) {
		    me.terminal_newline();
		}
		break;

	    default:
		throw RangeError("terminal inconsistency detected, cursor wrap overflow is set, but cursor wrap mode is "+me.cursor.wrap);
	    }

	}

	me.screen[me.cursor.position.y][me.cursor.position.x] = [ code, me.cursor.colours.slice() ];
	me.cursor.position.x++;
	if (me.cursor.position.x == me.width) {
	    if (me.cursor.wrap == 'simple'
		|| (me.cursor.wrap == 'bottom' && me.cursor.position.y < (me.height - 1))) {
		me.terminal_newline();
		return;
	    }

	    me.cursor.wrapOverflow = true;
	    me.cursor.position.x--;
	}
    },

    terminal_print_chars: function(chars) { // throws RangeError
	var me = this;

	for (var i = 0; i < chars.length; i++) {
	    var code = chars.charCodeAt(i);

	    if (code < 32) {
		// Special case for nonprintable characters < ASCII 32
		// So far only minimal support; only newline (10) implemented
		switch (code) {
		    case 10: me.terminal_newline(); break;
		    default: throw RangeError("Unsupported nonprintable character ASCII "+code); break
		}
	    }
	    else {
		me.terminal_print_char(code);
	    }
	}
    },

    terminal_newline: function() {
	var me = this;

	me.cursor.position.x = 0;
	if (++me.cursor.position.y == me.height) {
	    me.terminal_scroll_up();
	}
    },

    terminal_scroll_up: function(lines) {
	var me = this;

	lines = lines || 1;
	if (lines < 0 || lines > me.height) {
	    throw RangeError('Unsupported scroll distance, must be between 1 and '+me.height);
	}
	me.cursor.position.y -= lines;
	Array.prototype.push.apply(me.history, me.screen.slice(0, lines));
	me.screen = me.screen.slice(lines);
	while (lines--) {
	    me.screen[me.height - lines - 1] = new Array(me.width);
	    me.screen[me.height - lines - 1].fill([ me.defaults.glyph, me.cursor.colour.fg, me.cursor.colour.bg ]);
	}
    },

    debug: function() {
	var me = this;

	for (var y = 0; y < me.height; y++) {
	    var row = me.screen[y];
	    var out = [];
	    for (var x = 0; x < me.width; x++) {
		out.push(String.fromCodePoint(row[x][0]));
	    }
	    console.log(out.join(""));
	}
    },
});
