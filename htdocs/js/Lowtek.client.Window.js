Lowtek.util.ns('Lowtek.client');

Lowtek.client.Window = class Window extends Lowtek.Core {
    constructor(opts = {}) {
        super(opts);
        this.init();
    }

    get DEFAULTS() {
        return {
            /* screen is a 2d array representing the characters of the screen,
             * divided into rows and columns.  Each character is always an
             * array:
             * [ (int) unicode character, (array of int arrays) colours,
             *   (object) (any other data needed, can be omitted) ]
             */
            screen: null,
            width: null,
            height: null,
            maxHeight: null,
            cursor: null,
            wrap: true,
            scroll: true,
            position: null,
            canvas: null,
	    font: '9x15',
            parent: null,
            children: [],
            cursorVisible: false,
            
            defaults: {
                // What glyph to fill new windows with per default, what glyph to print
                // for rows that do not have a character at a given position
                glyph: 32,

                // What colours to paint with initially.  When a character is printed to
                // a cell, it will use the currently selected colours
                colours: [ [ 0, 0, 0, 255 ], [ 255, 255, 255, 255 ] ],

                // When the cursor is visible, a block is printed in reverse video at
                // its position.
                cursorVisible: false,
            },
        };
    }

    init() {
        let me = this;

        let screen = new Array(me.height);
        for (let i = 0; i < me.height; i++) {
            screen[i] = new Array(me.width);
            screen[i].fill([ me.glyph || me.defaults.glyph, me.colour || me.defaults.colours ]);
        }
        me.screen = screen;
        me.history = [];
        me.cursor = {
            position: { x: 0, y: 0 },
            colours: me.colour || me.defaults.colours.slice(),
            visible: me.cursorVisible || me.defaults.cursorVisible,
            truncate: false,
        }

        let fontData = Lowtek.data.font[me.font];
        let canvas = document.createElement('canvas');
        canvas.height = me.height * fontData.height;
        canvas.width = me.width * fontData.width;
        me.canvas = canvas;
    }

    clearScreen() {
        let me = this;
        
        let screen = new Array(me.height);
        for (let i = 0; i < me.height; i++) {
            screen[i] = new Array(me.width);
            screen[i].fill([ me.glyph || me.defaults.glyph, me.cursor.colours.slice() ]);
        }
        me.screen = screen;
        me.history = [];
        me.cursor.position = { x: 0, y: 0 };
    }
    
    receiveMessage(msg) { // throws Error
        let me = this;
        let handler = "handle_"+ msg.cmd.toLowerCase();

        if (me[handler]) {
            me[handler](msg);
        }
        else {
            // We don't know how to handle this command, so it must be invalid
            throw Error("invalid command '"+ msg.cmd +"' received");
        }
    }

    render() {
        // FIXME: Possible rendering optimisation, if a window has children, do not render itself?
        // FIXME: Rendering optimisation: Skip rendering of cells if we know nothing has changed, just
        //    return canvas.
        let me = this;

        // Render myself
        let ctx = me.canvas.getContext('2d');
        let fontData = Lowtek.data.font[me.font];
        let cpos = me.cursor.position;
        let cvis = me.cursor.visible;
        
        for (let y = 0; y < me.height; y++) {
            for (let x = 0; x < me.width; x++) {
                let cell = me.screen[y][x];
                let colours = (cvis && cpos.x == x && cpos.y == y) ? [ cell[1][1], cell[1][0] ] : cell[1];
                Lowtek.runtime.fontManager.render(
                    ctx, { y: y*fontData.height, x: x*fontData.width }, cell[0],
                    { font: me.font, colours }
                );
            }
        }

        // Render children and copy them into myself
        for (let child of me.children) {
            let ccanvas = child.render();
            ctx.drawImage(ccanvas, child.position.x * fontData.width, child.position.y * fontData.height);
        }
        
	return me.canvas;
    }

    addChild(name) {
        let me = this;
        me.children.push(name);
    }

    getSize() {
	let me = this;
        let fontData = Lowtek.data.font[me.font];

	return [ fontData.width * me.width, fontData.height * me.height ];
    }
    
    handle_output(msg) {
        let me = this;

        me.addCharacters(msg.data);
    }
    
    addCharacter(code) {
        let me = this;

        // Are we currently in truncate mode (because wrapping is not enabled)?
        if (me.cursor.truncate) {
            return;
        }
        
        me.screen[me.cursor.position.y][me.cursor.position.x] = [ code, me.cursor.colours.slice() ];
        me.cursor.position.x++;
        if (me.cursor.position.x == me.width) {
            if (me.wrap) {
                me.command_newline();
            }
            else {
                me.cursor.truncate = true;
                me.cursor.position.x--;
            }
        }
    }

    addCharacters(chars) { // throws RangeError
        let me = this;

        for (let i = 0; i < chars.length; i++) {
            let code = chars.charCodeAt(i);

            if (code < 32) {
                // Special case for nonprintable characters < ASCII 32
                // So far minimal support; only newline (10) implemented
                switch (code) {
                    case 10: me.command_newline(); break;
                    default: throw RangeError("Unsupported nonprintable character ASCII "+code); break
                }
            }
            else {
                me.addCharacter(code);
            }
        }
    }

    command_newline() {
        let me = this;

        me.cursor.position.x = 0;
        me.cursor.truncate = false;
        if (++me.cursor.position.y == me.height) {
            me.command_scroll_up();
        }
    }

    command_scroll_up(lines) { // throws RangeError
        let me = this;

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
    }

    command_cursor_left(cells = 1) {
        let me = this;
        
        while (cells-- && me.cursor.position.x > 0) {
            me.cursor.position.x--;
        }
    }

    command_set_cursor_at(x, y) {
        let me = this;
        me.cursor.position = { x, y };
    }
    
    debug() {
        let me = this;

        for (let y = 0; y < me.height; y++) {
            let row = me.screen[y];
            let out = [];
            for (let x = 0; x < me.width; x++) {
                out.push(String.fromCodePoint(row[x][0]));
            }
            console.log(out.join(""));
        }
    }
};
