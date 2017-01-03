/* PWM Terminal

This javascript application consists of two discrete parts; the
interpreter and the renderer.

The Interpreter deals with running a stream of UTF-8
characters through a simple VM, resulting in various functions being
executed, and a screen variable being populated with characters.

The Renderer renders the screen onto a HTML5 canvas using predefined
glyphs.

Please see each individual class for additional information.
*/

Lowtek.util.ns('Lowtek.pwm.client');

