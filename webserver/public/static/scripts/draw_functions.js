function intervalWebcamFrame (){
    // This draws the video then updates the bounding boxes. First offscreen rendering.
    ctxWcVideo.drawImage(video, 0, 0, wc_coords[2], wc_coords[3]);
    currentData = JSON.parse(tempData);
    var PADDING = 0;
    var x,y,w,h;
    var data = currentData;

    // update color code for classes
    updateDrawingTable(data);

    // Draw the bounding boxes
    if (data.type == "detection_data"){
        for (var j = 0, len2 = data.bbs.length; j < len2; ++j ){
            var bb = data.bbs[j];
            var text = data.classes[j];
            // Draw the rectangle that will contain the object name and confidence socre.
            ctxWcVideo.fillStyle = classesTable[text].color;
            x = bb[1];
            // Ensure that the rectangle is inside the allowable area.
            y = bb[0] + 0;
            w = bb[3] - bb[1];
            h = Math.ceil(y*TEXT_BOX_HEIGHT);
            ctxWcVideo.fillRect(x,y,w,h);

            // Draw the bounding box around the given obect
            ctxWcVideo.strokeStyle = classesTable[text].color;
            ctxWcVideo.strokeRect(bb[1],
              bb[0],
              bb[3] - bb[1] - PADDING,
              bb[2] - bb[0] - PADDING);

            // Draw the text inside the rectangle
            ctxWcVideo.font = bbTextSize + "pt Arial";
            ctxWcVideo.fillStyle = '#FFFFFF'
            ctxWcVideo.fillText(text,
                         x + 0, 
                         y + bbTextHPadding);
            let score = data.scores[j].toFixed(2)
            ctxWcVideo.fillText(score,
                          x + 0, 
                          y + bbTextHPadding*2);
        }
    }
        
      // Update the entire canvas
      ctx.drawImage(wcVideoCanvas, wc_coords[0], wc_coords[1], wc_coords[2], wc_coords[3]);
};
    

function updateDrawingTable(data) {
  for(let i=0; i<data.classes.length; i++){
    let className = data.classes[i]

    // generate hex color code for class
    if( !classesTable.hasOwnProperty(className) ){
      // generate color hex code for this class
      let color = '#'+(Math.random() * 0xFFFFFF << 0).toString(16).padStart(6, '0');
      classesTable[className] = {}
      classesTable[className]['color'] = color;
    }

    // update bounding box
    classesTable[className]['bbs'] = data.bbs[i];
    classesTable[className]['scores'] = data.scores[i];
  }
}





