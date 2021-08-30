// Video Stream Resolution and Screen Size
var resolutions = [[640,480],[1280,720]],
    resolution = resolutions[0],
    videoHeight = resolution[1],
    videoWidth = resolution[0],
    screenHeight = screen.height,
    screenWidth = screen.width,
    pc = new RTCPeerConnection(),
    video = document.querySelector('#live');
// Data Channel Communication
var dc = null,
    dcInterval = null;

// Canvas Coordinate Locations:
var wc_x, wc_y, wc_x_, wc_y_,
    wc_coords;

// Canvas Variables
// On Screen Canvas For all Draw Operations
var canvas = document.querySelector('#canvas'),
    canvasHeight, headerHeight,
    ctx = canvas.getContext('2d');
    ctx.strokeStyle = '#ff0';
    ctx.lineWidth = 2;
// Temporary offscreen canvas
var wcVideoCanvas = document.createElement('canvas'), 
    ctxWcVideo = wcVideoCanvas.getContext('2d');
    
   
// Update variables
const webcamUpdateIntervalMS = 100;

// ML Result DATA. 
var currentData = "{}",
    tempData = "{}";
var classesTable = {};

// Label Data
var TEXT_BOX_HEIGHT=0.2,
    bbTextSize=12,
    bbTextHPadding=bbTextSize + 1;

// Frontend debug
var DEBUG=0;
if(DEBUG){
    tempData = '{"type": "detection_data", "name": "YOLO Predictor Thread", "pc_id": "810c87c5-7b98-4709-879d-49bd14712695", "bbs": [[156.0, 224.0, 258.0, 248.0], [274.0, 405.0, 417.0, 429.0], [155.0, 302.0, 256.0, 325.0], [156.0, 224.0, 258.0, 248.0], [274.0, 405.0, 417.0, 429.0], [163.0, 156.0, 270.0, 181.0]], "scores": [0.9217681884765625, 0.8408660292625427, 0.8396438956260681, 0.8271344304084778, 0.7707495093345642, 0.5672974586486816], "classes": ["5s", "6s", "6s", "5c", "6c", "3c"]}';
}

