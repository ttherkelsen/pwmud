// Prepare the game to be started -- onLoad event must start the game
// Cannot rely on the DOM being fully formed at this point, but all
// necessary code has been loaded as this code is guaranteed to be the
// last code to be run prior to onLoad event

Lowtek.util.ns('Lowtek.runtime');

//Lowtek.runtime.game = new Lowtek.game.Game();
Lowtek.runtime.fontManager = new Lowtek.manager.Font();

//Lowtek.t = new Lowtek.terminal.ScreenVM({ height: 4, width: 10 });
//Lowtek.t.init()

Lowtek.runtime.setup = function() {
    var term = new Lowtek.terminal.Terminal({
	width: 80,
	height: 40,
	canvasId: 'pwm-canvas',
	font: '9x15',
    });

    term.input("This is a test\n");
    term.screen.cursor.colours[1] = [ 255, 0, 0, 255 ];
    term.input("This is a test\n");
    term.screen.cursor.colours[0] = [ 0, 0, 255, 255 ];
    term.input("This is a test\n");
    term.render();


    ws = Lowtek.runtime.websocket = new WebSocket('ws://lowtek.dk:4000/', 'pywebmud');
    ws.onopen = function(event) {
	console.log("WebSocket successfully opened.");
	ws.send(JSON.stringify({ type: 'init', message: 'this is a test message' }));
    };
    ws.onmessage = function(event) {
	console.log(event.data);
    };
}

