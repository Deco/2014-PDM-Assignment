
var followMouse = false;
var mouseMoved = false;
var mousePos = { x: -1, y: -1 };

var eyeList = [
    { x: 0.260, y: 0.163, outlineCircleEl: null, bigCircleEl: null, innerCircleEl: null },
    { x: 0.309, y: 0.167, outlineCircleEl: null, bigCircleEl: null, innerCircleEl: null },
    
    { x: 0.472, y: 0.166, outlineCircleEl: null, bigCircleEl: null, innerCircleEl: null },
    { x: 0.525, y: 0.166, outlineCircleEl: null, bigCircleEl: null, innerCircleEl: null },
    
    { x: 0.725, y: 0.168, outlineCircleEl: null, bigCircleEl: null, innerCircleEl: null },
    { x: 0.776, y: 0.166, outlineCircleEl: null, bigCircleEl: null, innerCircleEl: null },
];

function makeGooglyEyes() {
    for (var i = 0; i < eyeList.length; i++) {
        var eye = eyeList[i];
        eye.outlineCircleEl   = $('<div class="eyeOutlineCircle"></div>');
        eye.bigCircleEl       = $('<div class="eyeBigCircle"    ></div>');
        eye.innerCircleEl     = $('<div class="eyeInnerCircle"  ></div>');
        $("body").append(eye.outlineCircleEl);
        $("body").append(eye.bigCircleEl);
        $("body").append(eye.innerCircleEl);
    }
}

var outlineCircleScale = 0.045;
var bigCircleScale = 0.040;
var smallCircleScale = 0.035;

function positionGooglyEyes() {
    var logoOffset = $("#logo").offset();
    var logoWidth  = $("#logo").width ();
    var logoHeight = $("#logo").height();
    for (var i = 0; i < eyeList.length; i++) {
        var eye = eyeList[i];
        var bigSize = logoWidth*outlineCircleScale;
        eye.outlineCircleEl
            .offset({ top: logoOffset.top+eye.y*logoHeight-bigSize/2, left: logoOffset.left+eye.x*logoWidth-bigSize/2 })
            .css("width", bigSize).css("height", bigSize)
        ;
        var size = logoWidth*bigCircleScale;
        eye.bigCircleEl
            .offset({ top: logoOffset.top+eye.y*logoHeight-size/2, left: logoOffset.left+eye.x*logoWidth-size/2 })
            .css("width", size).css("height", size)
            //.css("outline-width", logoWidth*outlineScale)
        ;
        var size = logoWidth*smallCircleScale;
        var rx = logoOffset.left+eye.x*logoWidth;
        var ry = logoOffset.top+eye.y*logoHeight;
        if(mouseMoved) {
            var ang = Math.atan2(mousePos.y-ry, mousePos.x-rx);
            rx += Math.cos(ang)*(bigSize-size);
            ry += Math.sin(ang)*(bigSize-size);
        } else {
            size = size*0.8;
        }
        eye.innerCircleEl
            .offset({ top: ry-size/2, left: rx-size/2 })
            .css("width", size).css("height", size)
        ;
    }
}

$(window).load(function() {
    setTimeout(function() {
        makeGooglyEyes();
        positionGooglyEyes();
        $(window).resize(positionGooglyEyes);
        $(window).scroll(positionGooglyEyes);
    }, 10000);
    setTimeout(function() {
        followMouse = true;
    }, 14000);
    $(document).mousemove(function(event) {
        if(followMouse) {
            mousePos.x = event.pageX;
            mousePos.y = event.pageY;
            mouseMoved = true;
            positionGooglyEyes();
        }
    });
});
