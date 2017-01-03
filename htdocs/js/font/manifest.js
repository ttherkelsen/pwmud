/*
 * This file contains a manifest over all fonts known by the PWMud client.
 *
 */

Lowtek.util.ns('Lowtek.data', 'Lowtek.runtime');

Lowtek.data.font = {
    "9x15": {
	name: "9x15",

	/* How many bits each pixel of the bitmap occupies.  Eg., a bit
	 * depth of 1 means each pixel uses 1 bit, hence 2 colours are
	 * possible for each bit, and 8 pixels can be encoded in a byte.
	 */
	bitdepth: 1,
	width: 9,
	height: 15,
	colour: [ // RGBA colours, default renderer settings
	    [   0,   0,   0, 255 ],
	    [ 255, 255, 255, 255 ],
	],
	unknownGlyph: 0, // Which glyph to use if an unknown glyph is requested
	glyph: {
	    /* unicode number for glyph: [ row 1 bits, row 2 bits... ] */
	}
    },
};

/* font name - colour list : font code page rendered to canvas */
Lowtek.runtime.fontcache = {};

