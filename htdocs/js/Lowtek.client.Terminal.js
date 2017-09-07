Lowtek.util.ns('Lowtek.terminal');

Lowtek.client.Terminal = class Terminal extends Lowtek.Core {
    constructor(opts = {}) {
        super(opts);
        
        let me = this;
        me.init();
    }

    get DEFAULTS() {
        return {
            canvasId: null,
            canvas: null,
            windows: {},
            width: null,
            height: null,
            font: null,
            currentWindow: null,
        };
    }
    
    init() {
        let me = this;
        let fontData = Lowtek.data.font[me.font];

        me.addWindow('root', {
            position: { x: 0, y: 0 },
            height: me.height,
            width: me.width,
        });
        
        me.canvas = document.getElementById(me.canvasId);
        [ me.canvas.width, me.canvas.height ] = me.windows['root'].getSize();
    }

    receiveMessage(msg) {
        let me = this;
        let handler = "handle_"+ msg.cmd.toLowerCase();

        if (me[handler]) {
            me[handler](msg);
        }
        else {
            // We don't know how to handle this command, delegate to window
            let target = msg.window || me.currentWindow;
            let win;
            
            if (!target || !(win = me.windows[target])) {
                console.log("Can't delegate message since no window exists.", msg);
                return;
            }
            
            win.receiveMessage(msg);
        }
    }

    handle_set_active_window(msg) {
        let me = this;
        me.currentWindow = msg.data.window;
    }

    handle_add_window(msg) {
        let me = this;
        let data = msg.data;
        
	me.addWindow(data.id, data);
    }
  
    render() {
        let me = this;
        let wcanvas = me.windows['root'].render();
        let ctx = me.canvas.getContext("2d");

        ctx.drawImage(wcanvas, 0, 0);
    }

    addWindow(name, opts = {}) {
        let me = this;
        
        me.windows[name] = new Lowtek.client.Window(
            Object.assign({}, opts)
        );
        me.currentWindow = name;
        if (opts.parent) {
            me.windows[opts.parent].addChild(me.windows[name]);
        }
    }
};
