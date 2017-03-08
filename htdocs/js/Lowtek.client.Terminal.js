Lowtek.util.ns('Lowtek.terminal');

Lowtek.client.Terminal = function(opts) {
    var me = this;

    Lowtek.Core.call(me, opts);
    me.init();
};

Lowtek.util.inherit(Lowtek.client.Terminal, Lowtek.Core);

Lowtek.util.merge(Lowtek.client.Terminal.prototype, {
    canvasId: null,
    canvas: null,
    windows: {},
    width: null,
    height: null,
    font: null,
    currentWindow: null,
    windowDefaults: {
	// What glyph to fill new windows with per default, what glyph to print
	// for rows that do not have a character at a given position
	glyph: 32,

	// What colours to paint with initially.  When a character is printed to
	// a cell, it will use the currently selected colours
	colours: [ [ 0, 0, 0, 255 ], [ 255, 255, 255, 255 ] ],

	// When the cursor is visible, a block is printed in reverse video at
	// its position.
	cursorVisible: true,

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
	// expand - FIXME never wrap, extend row size instead (this will create a
	//     horizontal scrollbar) 
	wrap: 'simple',
	wrapOverflow: false,
    },

    init: function() {
	var me = this;
	var fontData = Lowtek.data.font[me.font];

	me.addWindow('root', { x: 0, y: 0, h: me.height, w: me.width });
	
	me.canvas = document.getElementById(me.canvasId);
	me.canvas.width = me.width * fontData.width;
	me.canvas.height = me.height * fontData.height;
    },

    input: function(chars) {
	var me = this;
	var stream = chars.split("\x07");
	var funcMode = false;
	
	for (var i = 0; i < stream.length; i++) {
	    if (funcMode) {
		var functions = stream[i].split("\x08");

		for (var j = 0; j < functions.length; i++) {
		    me.handleCommand(functions[j]);
		}
	    }
	    else {
		me.command_print_chars(stream[i]);
	    }
	    funcMode = !funcMode;
	}
    },

    render: function() {
	var me = this;
	var ctx = me.canvas.getContext('2d');
	var fontData = Lowtek.data.font[me.font];

	for (var y = 0; y < me.height; y++) {
	    for (var x = 0; x < me.width; x++) {
		cell = me.screen.screen[y][x];
		Lowtek.runtime.fontManager.render(
		    ctx, { y: y*fontData.height, x: x*fontData.width }, cell[0],
		    { font: me.font, colours: cell[1] }
		);
	    }
	}
    },

    addWindow: function(name, bbox, opts) {
	me.windows[name] = new Lowtek.client.Window(
	    Lowtek.utils.merge(me.windowDefaults, opts || {}, { bbox: bbox })
	);
	me.currentWindow = name;
    },

    handleCommand: function(cmdstr) { // throws Error
	var me = this;
	var parts, cmd;
	
	if (!cmdstr) return;

	cmdstr = cmdstr.replace("\\;", "\x08");
	parts = cmdstr.split(";").map(function(e) { return e.replace("\x08", ";"); });

	if (!me[cmd = 'command_'+ parts[0]]) {
	    throw Error("Invalid command" + parts[0]);
	}
	me[cmd].apply(me, parts);
    },

    command_print_chars: function(chars) {
	var me = this;
	
	if (!chars) return;
	
	me.windows[me.currentWindow].addCharacters(chars);
    },
});
