Lowtek.util.ns('Lowtek.terminal');

Lowtek.terminal.Terminal = function(opts) {
    var me = this;

    Lowtek.Core.call(me, opts);
    me.init();
};

Lowtek.util.inherit(Lowtek.terminal.Terminal, Lowtek.Core);

Lowtek.util.merge(Lowtek.terminal.Terminal.prototype, {
    canvasId: null,
    canvas: null,
    screen: null,
    width: null,
    height: null,
    font: null,

    init: function() {
	var me = this;
	var fontData = Lowtek.data.font[me.font];

	me.screen = new Lowtek.terminal.ScreenVM({ height: me.height, width: me.width });
	me.canvas = document.getElementById(me.canvasId);
	me.canvas.width = me.width * fontData.width;
	me.canvas.height = me.height * fontData.height;
    },

    input: function(chars) {
	var me = this;

	me.screen.addCharacters(chars);
	me.screen.parseStream();
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
});
