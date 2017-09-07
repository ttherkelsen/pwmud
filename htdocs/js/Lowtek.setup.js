// Prepare the game to be started -- a separate onLoad event must
// start the game.
//
// Cannot rely on the DOM being fully formed at this point, but all
// necessary code has been loaded as this code is guaranteed to be the
// last code to be run prior to onLoad event

Lowtek.util.ns('Lowtek.runtime');

//Lowtek.runtime.game = new Lowtek.game.Game();
Lowtek.runtime.fontManager = new Lowtek.manager.Font();

//Lowtek.t = new Lowtek.terminal.ScreenVM({ height: 4, width: 10 });
//Lowtek.t.init()

Lowtek.runtime.setup = function() {
    Lowtek.runtime.client = new Lowtek.client.Client({ url: 'ws://lowtek.dk:4000/', protocol: 'pywebmud' });
    return;
    
    let term = new Lowtek.terminal.Terminal({
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
}

