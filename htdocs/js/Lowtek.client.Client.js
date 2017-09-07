Lowtek.util.ns('Lowtek.client');

Lowtek.client.Client = class Client extends Lowtek.Core {
    constructor(opts = {}) {
        super(opts);
                
        let me = this;
        me.init();
    }

    get DEFAULTS() {
        return {
            version: 'PWMud corelib 0.1a',
            terminals: {},
            defaultTerminal: null,
            websocket: null,
            protocol: null,
            url: null,
            inputStack: [],
            renderFPS: 60,
        }
    }
    
    init() {
        let me = this;

        me.websocket = new WebSocket(me.url, me.protocol);
        me.websocket.onopen = e => me.wsOnOpen(e);
        me.websocket.onmessage = e => me.wsOnMessage(e);
        me.websocket.onerror = e => me.wsOnError(e);
        me.websocket.onclose = e => me.wsOnClose(e);

	window.addEventListener('keydown', e => me.onKeyDown(e));
	
        //me.renderLoop();
    }

    renderLoop() {
        let me = this;

        me.render();
        window.setTimeout(() => me.renderLoop(), 1000 / me.renderFPS);
    }
    
    render() {
        let me = this;

        for (let [id, term] of Lowtek.util.objectEntries(me.terminals)) {
            term.render();
        }
    }
    
    receiveMessage(msg) {
        let me = this;

        // FIXME: Add support for multiple commands in a single message (array)
        if (typeof(msg) === 'string') {
            msg = { 'cmd': 'output', 'data': msg };
        }
        
        let handler = "handle_"+ msg.cmd.toLowerCase();

        if (me[handler]) {
            me[handler](msg);
        }
        else {
            // We don't know how to handle this command, delegate to active terminal
            let target = msg.terminal || me.defaultTerminal;
            let term;
            
            if (!target || !(term = me.terminals[target])) {
                console.log("Can't delegate message since no terminal exists.", msg)
                return;
            }

            term.receiveMessage(msg);
        }
        me.render(); // FIXME: temp fix
    }

    sendMessage(msg) {
        var me = this;

        me.debug("sendMessage", msg);
        me.websocket.send(JSON.stringify(msg));
    }
    
    handle_query(msg) {
        let me = this;
        let response;
        
        switch (msg.query) {
        case 'version':
            response = me.version;
            break;
        default:
            console.log("Unsupported query", msg)
            return;
        }

        me.sendMessage({ cmd: 'response', response: response, id: msg.id })
    }

    handle_response(msg) {
        // FIXME: So far the server does not support the client querying anything
        // from the server, but that may change in the future
        console.log("Unexpect response message:", msg);
    }

    handle_add_terminal(msg) {
        let me = this;
        me.terminals[msg.data.id] = new Lowtek.client.Terminal({
            font: msg.data.font,
            canvasId: msg.data.id,
            width: msg.data.width,
            height: msg.data.height,
        });
        me.defaultTerminal = msg.data.id;
        me.terminals[msg.data.id].init();
    }

    handle_push_input(msg) {
        let me = this;

        // FIXME: Test that terminal and window are valid
        me.inputStack.push(Object.assign({}, msg.data));
        me.initInput();
    }

    initInput() {
        let me = this;
        let data = me.getCurrentInput();

        data = Object.assign(data, { input: '', position: 0 })
        // FIXME: Only support for line mode (client side editing) so far
        if (data.mode == 'line') {
            me.updateInputLine();
        }
    }

    getCurrentInput() {
        let me = this;
        return me.inputStack[me.inputStack.length - 1];
    }

    updateInputLine() {
        let me = this;
        let data = me.getCurrentInput();
        let win = me.terminals[data.terminal].windows[data.window];

        win.clearScreen();
        win.addCharacters(data.prompt + data.input);
        win.command_set_cursor_at(data.position + data.prompt.length, 0);
        me.render(); // FIXME: temp hack
    }
    
    onKeyDown(event) {
        let me = this;
        
        event.preventDefault();
        /*
        Presently, this keyboard input handler is written to support
        Chrome.  Other browsers may behave in the same fashion, but
        this has not been tested.  The following are assumptions of
        keyboard behaviour that Chrome exposes, which will need to be
        tested in other browsers, too:

        1 - The browser (possibly through an OS mechanism) is handling
        key repeats.  All keys repeat, even modifier keys like Shift.

        2 - The value in event.key will always be 1 character if the
        event corresponds to a printable character.

        3 - The value in event.key will always be more than 1
        character if the event corresponds to a non-printable
        character (eg., F5 or Shift).
        */
        
        let data = me.getCurrentInput();
        let win = me.terminals[data.terminal].windows[data.window];
        
        if (event.key.length == 1) {
            // FIXME: We can only handle 1 line of input presently
            data.input = data.input.substr(0, data.position) + event.key + data.input.substr(data.position)
            data.position++;
            me.updateInputLine();
            return;
        }

        switch (event.key) {
        case 'ArrowLeft':
            if (data.position > 0) data.position--;
            break;
        case 'ArrowRight':
            if (data.position < data.input.length) data.position++;
            break;

        case 'Backspace':
            if (data.position > 0) {
                data.position--;
                data.input = data.input.substr(0, data.position) + data.input.substr(data.position + 1);
            }
            break;
        case 'Delete':
            if (data.position < data.input.length) {
                data.input = data.input.substr(0, data.position) + data.input.substr(data.position + 1);
            }
            break;

        case 'Home':
            data.position = 0;
            break;
        case 'End':
            data.position = data.input.length;
            break;

        case 'Enter':
            me.sendMessage({ cmd: 'input', data: data.input });
            me.initInput();
            break;
            
        default: console.log(event); break;
        }

        me.updateInputLine();
    }
    
    wsOnOpen(event) {
        console.log("WebSocket successfully opened.", event);
    }

    wsOnMessage(event) {
        let me = this;
        let msg = JSON.parse(event.data);

        console.log("WebSocket message received", msg)
        me.receiveMessage(msg);
    }

    wsOnError(event) {
        console.log("WebSocket error", event);
    }

    wsOnClose(event) {
        console.log("WebSocket closed", event);
    }
};
