"""
画像処理を行うスクリプト
"""

import cv2
import numpy as np
import base64

from src.segmentation import DeepLabModel


def edit_gamma_contrast(in_img):
    """Edit gamma for good looks.

    Args:
        in_img: input image. [color-order: 'BGR']
    Returns:
        [color-order: 'BGR']
    """

    # ガンマ補正用テーブル
    gamma = 1 / np.sqrt(in_img.mean()) * 15  # PARAMETER
    g_table = np.array(
        [((i / 255.0) ** (1 / gamma)) * 255 for i in np.arange(0, 256)]
    ).astype("uint8")

    # ガンマ補正
    img_gamma = cv2.LUT(in_img, g_table)

    return img_gamma


def crop_image(image, rects):
    """Crop images with guide from frontend

    Args:
        image: an input image [BGR]
        rects: guide of where are persons
    Returns:
        List of cropped images [BGR](same sized)
    """
    imgs_cropped = []
    for rect in rects:
        crop_img = image[
            int(rect["y"]) : int(rect["y"]) + int(rect["h"]),
            int(rect["x"]) : int(rect["x"]) + int(rect["w"]),
        ]
        imgs_cropped.append(crop_img)

    return imgs_cropped


def decode_img(img_base64):
    """decode from base64 into png

    Args:
        img_base64: base64
    Returns:
        a png image
    """
    img_png = base64.b64decode(img_base64)
    img_png = np.frombuffer(img_png, dtype=np.uint8)
    img_png = cv2.imdecode(img_png, cv2.IMREAD_COLOR)
    return img_png


def encode_img(img_png):
    """encode from a png image into base64

    Args:
        img_png: single png[RGBA] image
    Returns:
        encoded base64
    """
    img_png_rbga = cv2.cvtColor(img_png, cv2.COLOR_RGBA2BGRA)
    retval, png = cv2.imencode(".png", img_png_rbga)
    encoded = base64.b64encode(png.tostring())
    return encoded


def main(img_base64, rects):
    """Entroy point. Implement image processing.

    Args:
        image_binary: binary encoded png image.
        rects: shows where are each person.
    Returns:
        processed image (number is human number)
    """

    # ------1.---------

    # decode from base64 into png
    img_original = decode_img(img_base64)

    # from png to BGR
    img_original_bgr = cv2.cvtColor(img_original, cv2.COLOR_RGBA2BGR)

    # crop image with guide
    imgs_cropped = crop_image(img_original_bgr, rects)

    # -------2.-------

    # edit image light (BGR to BGR)
    imgs_editted = [edit_gamma_contrast(image) for image in imgs_cropped]

    # do segmentation (RGB to png [RGBA])
    imgs_editted_rgb = [
        cv2.cvtColor(image, cv2.COLOR_BGR2RGB) for image in imgs_editted
    ]
    seg_model = DeepLabModel()
    imgs_seged = seg_model.run(imgs_editted_rgb)

    # -------3.---------

    # encode from png to binary
    imgs_encoded = [encode_img(image) for image in imgs_seged]

    # return binary png image
    return imgs_encoded
