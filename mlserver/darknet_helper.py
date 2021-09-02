def convert2relative(bbox, darknet_height, darknet_width):
    """
    YOLO format use relative coordinates for annotation
    """
    x, y, w, h  = bbox
    return x/darknet_width, y/darknet_height, w/darknet_width, h/darknet_height


def convert2original(image, bbox, darknet_height, darknet_width):
    x, y, w, h = convert2relative(bbox, darknet_height, darknet_width)

    image_h, image_w, __ = image.shape

    orig_x       = int(x * image_w)
    orig_y       = int(y * image_h)
    orig_width   = int(w * image_w)
    orig_height  = int(h * image_h)

    bbox_converted = (orig_x, orig_y, orig_width, orig_height)

    return bbox_converted