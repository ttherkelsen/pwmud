Lowtek.util.ns('Lowtek.client');

Lowtek.client.Client = function(opts) {
    var me = this;

    Lowtek.Core.call(me, opts);
    me.init();
};

Lowtek.util.inherit(Lowtek.client.Client, Lowtek.Core);

Lowtek.util.merge(Lowtek.client.Client.prototype, {
    version: 'PWMud 0.1a',
    terminals: null,
    defaultTerminal: null,
    websocket: null,
    protocol: null,
    url: null,

    init: function() {
	var me = this;

	me.terminals = {};
	me.websocket = new WebSocket(me.url, me.protocol);
	me.websocket.onopen = me.wsOnOpen;
	me.websocket.onmessage = me.wsOnMessage;
	me.websocket.onerror = me.wsOnError;
	me.websocket.onclose = me.wsOnClose;
    },

    receiveMessage: function(msg) {
	var me = this;
	var handler = "handle_"+ msg.type.toLowerCase();

	if (!me[handler]) {
	    console.log("Invalid message received:", msg);
	    return;
	}

	me[handler](msg);
    },

    sendMessage: function(msg) {
	me.websocket.send(JSON.stringify(msg))
    },
    
    handle_output: function(msg) {
	var me = this;
	var term;
	
	// FIXME: Handle msg.terminal override instead of using me.defaultTerminal
	if (!me.defaultTerminal || !(term = me.terminals[me.defaultTerminal])) {
	    console.log("Output message received but no terminal exists.", msg)
	    return;
	}
	term.input(msg.msg);
	term.render();
    },

    handle_command: function(msg) {
	var me = this;
	var handler = "command_" + msg.command.toLowerCase();

	if (!me[handler]) {
	    console.log("Invalid command message:", msg);
	    return;
	}

	me[handler](msg);
    },

    handle_query: function(msg) {
	var me = this;
	var response;
	
	switch (msg.query) {
	case 'version':
	    response = me.version;
	    break;
	default:
	    console.log("Unsupported query", msg)
	    return;
	}

	me.sendMessage({ type: 'response', response: response, id: msg.id })
    },

    handle_response: function(msg) {
	// FIXME: So far the server does not support the client querying anything
	// from the server, but that may change in the future
	console.log("Unexpect response message:", msg);
    },

    command_add_terminal: function(msg) {
	me.terminals[msg.id] = new Lowtek.terminal.Terminal({
	    font: msg.font,
	    canvasId: msg.id,
	    width: msg.size[0],
	    height: msg.size[1],
	});
	me.defaultTerminal = msg.id;
	me.terminals[msg.id].init();
    },
    
    wsOnOpen: function(event) {
	console.log("WebSocket successfully opened.", event);
    },

    wsOnMessage: function(event) {
	var me = this;
	var msg = JSON.parse(event.data);
	
	console.log(msg);
	me.receiveMessage(msg);
    },

    wsOnError: function(event) {
	console.log("WebSocket error", event);
    },

    wsOnClose: function(event) {
	console.log("WebSocket closed", event);
    },
});
