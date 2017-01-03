Lowtek.util.ns('Lowtek.gui');

Lowtek.gui.Font = function(opts) {
    var me = this;

    Lowtek.Core.call(me, opts);
    me.fontData = Lowtek.data.font[opts.font];
    me.loadFont();
};

Lowtek.util.inherit(Lowtek.gui.Font, Lowtek.Core);

Lowtek.util.merge(Lowtek.gui.Font.prototype, {
    font: null,
    colours: null,
    
    layout: function(text) {
	// FIXME: Wrapping? Support for proportional fonts
	var me = this;
	var size = { h: me.fontData.height, w: me.fontData.width * text.length };
	return size;
    },

    render: function(text, canvas, offset) {
	var me = this;
	var ctx = canvas.getContext("2d");
	text = text.split('');
	offset = offset || { x: 0, y: 0 };
	
	for (var i = 0; i < text.length; i++) {
	    var glyph = text[i];
	    var index = me.fontData.glyphIndex.indexOf(glyph);

	    if (index == -1) {
		index = 0;
	    }
	    else {
		index++;
	    }

	    ctx.drawImage(
		me.canvas,
		index*me.fontData.width, 0, me.fontData.width, me.fontData.height, // source
		offset.x + i*me.fontData.width, offset.y, // destination position
		me.fontData.width, me.fontData.height // destination size
	    );
	}
    },

    loadFont: function() {
	var me = this;
	var index = me.fontData.glyphIndex.split("");
	var canvas = document.createElement("canvas");
	canvas.height = me.fontData.height;
	canvas.width = me.fontData.width * (index.length + 1);
	var ctx = canvas.getContext("2d");

	me.colours = Lowtek.util.merge({}, me.fontData.colours, me.colours || {});
	me.renderGlyph(ctx, { x: 0, y: 0 }, '__UNKNOWN__', me.colours);
	for (var i = 0; i < index.length; i++) {
	    me.renderGlyph(ctx, { x: (i + 1)*me.fontData.width, y: 0 }, index[i], me.colours);
	};

	me.canvas = canvas;
	me.ctx = ctx;
    },

    renderGlyph: function(ctx, pos, glyph, colours) {
	var me = this;
	var img = ctx.createImageData(me.fontData.width, me.fontData.height);
	var glyphData = me.fontData.glyphs[glyph];
	colours = colours || me.fontData.colours;
	
	if (!glyphData) glyphData = me.fontData.glyphs.__UNKNOWN__;

	for (var y = 0; y < me.fontData.height; y++) {
	    var row = glyphData[y].split('');
	    for (var x = 0; x < me.fontData.width; x++) {
		var colour = colours[glyphData[y][x]];
		
		if (!colour) colour = me.fontData.colours.__UNKNOWN__;
		for (var i = 0; i < 4; i++) {
		    img.data[y*me.fontData.width*4 + x*4 + i] = colour[i];
		}
	    }
	}
	ctx.putImageData(img, pos.x, pos.y);
    },
});
