Lowtek.util.ns('Lowtek.manager');

Lowtek.manager.Font = class Font extends Lowtek.Core {
    constructor(opts = {}) {
        super(opts);
    }

    get DEFAULTS() { return {}; }
    
    /* Render font glyphs to the 2d canvas ctx, starting at coordinate
     * pos, using the font settings given */
    render(ctx, pos, glyphs, settings) {
        let me = this;
        let x = pos.x, y = pos.y;
        settings = settings || { font: '9x15', colours: [ [ 0, 0, 0, 255 ], [ 255, 255, 255, 255 ] ] };
        let fontData = Lowtek.data.font[settings.font];

        if (typeof glyphs == 'number') glyphs = [ glyphs ];

        // FIXME: Should probably split the code based on whether glyphs is a string or an array
        for (let i = 0; i < glyphs.length; i++) {
            let glyph = (typeof glyphs[i] == 'string') ? glyphs.charCodeAt(i) : glyphs[i];
            let index = glyph % 256;
            let page = me.getFontGlyphPage(glyph, settings);
            
            ctx.drawImage(
                page, // source ctx
                index*fontData.width, 0, fontData.width, fontData.height, // src: x, y, width, height
                x + i*fontData.width, y, fontData.width, fontData.height // dst: x, y, width, height
            );
        }
    }

    getFontGlyphPage(glyph, settings) {
        let me = this;
        let colours = settings.colours || Lowtek.data.font[settings.font].colour
        let cachestr = settings.font + JSON.stringify(settings.colours)
        let tmp, tmp2;

        // Is it already cached?
        if ((tmp = Lowtek.runtime.fontcache[cachestr]) && (tmp2 = tmp[glyph >> 8])) {
            return tmp2;
        }

        if (!tmp) {
            tmp = Lowtek.runtime.fontcache[cachestr] = {};
        }
        
        return tmp[glyph >> 8] = me.getFontPage(glyph >> 8, settings.font, colours);
    }

    getFontPage(page, font, colours) {
        let fontData = Lowtek.data.font[font];
        let canvas = document.createElement('canvas');
        canvas.height = fontData.height;
        canvas.width = fontData.width * 256;
        let ctx = canvas.getContext('2d');
        let img = ctx.createImageData(fontData.width * 256, fontData.height);
        let bitmask = (fontData.bitdepth << 1) - 1;

        for (let i = 0; i < 256; i++) {
            let bitmap = fontData.glyph[page * 256 + i] || fontData.glyph[fontData.unknownGlyph];
            for (let y = 0; y < fontData.height; y++) {
                let row = bitmap[y];
                for (let x = 0; x < fontData.width; x++) {
                    let colour = colours[row & bitmask];
                    let j = 4;
                    while (j--) img.data[i*fontData.width*4 + y*fontData.width*4*256 + (fontData.width - x - 1)*4 + j] = colour[j];
                    row >>= fontData.bitdepth;
                }
            }
        }

        ctx.putImageData(img, 0, 0);
        return canvas;
    }
};
