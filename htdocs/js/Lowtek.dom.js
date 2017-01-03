// Various DOM methods

Lowtek.util.ns('Lowtek.dom');

Lowtek.dom.getOffset = function(element) {
    var o = { x: 0, y: 0 };
    
    while (element) {
	o.x += element.offsetLeft;
	o.y += element.offsetTop;
	element = element.offsetParent;
    }
    
    return o;
};
