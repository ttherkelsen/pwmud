Lowtek.util.ns('Lowtek.manager');

Lowtek.manager.Font = function(opts) {
    var me = this;

    Lowtek.Core.call(me, opts);
};

Lowtek.util.inherit(Lowtek.manager.Font, Lowtek.Core);

Lowtek.util.merge(Lowtek.manager.Font.prototype, {
    /* Render font glyphs to the 2d canvas ctx, starting at coordinate
     * pos, using the font settings given */
    render: function(ctx, pos, glyphs, settings) {
	var me = this;
	var x = pos.x, y = pos.y;
	settings = settings || { font: '9x15', colours: [ [ 0, 0, 0, 255 ], [ 255, 255, 255, 255 ] ] };
	var fontData = Lowtek.data.font[settings.font];

	if (typeof glyphs == 'number') glyphs = [ glyphs ];

	// FIXME: Should probably split the code based on whether glyphs is a string or an array
	for (var i = 0; i < glyphs.length; i++) {
	    var glyph = (typeof glyphs[i] == 'string') ? glyphs.charCodeAt(i) : glyphs[i];
	    var index = glyph % 256;
	    var page = me.getFontGlyphPage(glyph, settings);
	    
	    ctx.drawImage(
		page, // source ctx
		index*fontData.width, 0, fontData.width, fontData.height, // src: x, y, width, height
		x + i*fontData.width, y, fontData.width, fontData.height // dst: x, y, width, height
	    );
	}
    },

    getFontGlyphPage: function(glyph, settings) {
	var me = this;
	var colours = settings.colours || Lowtek.data.font[settings.font].colour
	var cachestr = settings.font + JSON.stringify(settings.colours)
	var tmp, tmp2;

	// Is it already cached?
	if ((tmp = Lowtek.runtime.fontcache[cachestr]) && (tmp2 = tmp[glyph >> 8])) {
	    return tmp2;
	}

	if (!tmp) {
	    tmp = Lowtek.runtime.fontcache[cachestr] = {};
	}
	
	return tmp[glyph >> 8] = me.getFontPage(glyph >> 8, settings.font, colours);
    },

    getFontPage: function(page, font, colours) {
	var fontData = Lowtek.data.font[font];
	var canvas = document.createElement('canvas');
	canvas.height = fontData.height;
	canvas.width = fontData.width * 256;
	var ctx = canvas.getContext('2d');
	var img = ctx.createImageData(fontData.width * 256, fontData.height);
	var bitmask = (fontData.bitdepth << 1) - 1;

	for (var i = 0; i < 256; i++) {
	    var bitmap = fontData.glyph[page * 256 + i] || fontData.glyph[fontData.unknownGlyph];
	    for (var y = 0; y < fontData.height; y++) {
		var row = bitmap[y];
		for (var x = 0; x < fontData.width; x++) {
		    var colour = colours[row & bitmask];
		    var j = 4;
		    while (j--) img.data[i*fontData.width*4 + y*fontData.width*4*256 + (fontData.width - x - 1)*4 + j] = colour[j];
		    row >>= fontData.bitdepth;
		}
	    }
	}

	ctx.putImageData(img, 0, 0);
	return canvas;
    },
});
