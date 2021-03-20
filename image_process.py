"""
一連の処理をまとめた、デプロイ用のファイル
"""

import cv2
import numpy as np
import base64

from segmentation import DeepLabModel


def edit_gamma_contrast(in_img):
    """Edit gamma and contrast for good looks.

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
    # コントラスト補正用テーブル
    a = 10  # PARAMETER
    c_table = np.array(
        [255.0 / (1 + np.exp(-a * (i - 128) / 255)) for i in np.arange(0, 256)]
    ).astype("uint8")

    # ガンマ補正
    img_gamma = cv2.LUT(in_img, g_table)
    # コントラスト補正
    img_gamma = cv2.LUT(img_gamma, c_table)

    return img_gamma


def crop_image(images, guide):
    """Crop (trim) images with guide from frontend

    Args:
        images:
    Returns:
        List of cropped images(same sized)
    """
    # TODO: 実装！！


def decode_img(img_base64):
    """decode from base64 string into png

    Args:
        img_base64: base64 string
    Returns:
        a png image
    """
    img_png = base64.b64decode(img_base64)
    img_png = np.frombuffer(img_png, dtype=np.uint8)
    img_png = cv2.imdecode(img_png, cv2.IMREAD_COLOR)
    return img_png


def encode_img(img_png):
    """encode from a png image into base64 string

    Args:
        img_png: single png[RGBA] image
    Returns:
        encoded base64 string
    """
    retval, png = cv2.imencode(".png", img_png)
    encoded = base64.b64encode(png.tostring())
    return encoded


def main(img_base64=None):
    """Implement image processing

    Args:
        image_binary: binary encoded png image.
        guide: shows where are each person.
    Returns:
        processed image (number is human number)
    """

    # ------1. (honban)---------

    # decode from base64 string into png
    # TODO:
    img_original = decode_img(img_base64)

    # from png to BGR
    img_original_bgr = cv2.cvtColor(img_original, cv2.COLOR_RGBA2BGR)

    # crop image with guide
    imgs_cropped = crop_image(img_original_bgr)

    # -------1. (debug)----------

    # imgs_cropped = []
    # for i in range(10):
    #     img_read = cv2.imread(f"img/crop{i+1}.png")
    #     assert img_read is not None
    #     imgs_cropped.append(img_read)

    # -------2.-------

    # edit image light (BGR to BGR)
    imgs_editted = [edit_gamma_contrast(image) for image in imgs_cropped]

    # do segmentation (RGB to png [RGBA])
    imgs_editted_rgb = [
        cv2.cvtColor(image, cv2.COLOR_BGR2RGB) for image in imgs_editted
    ]
    seg_model = DeepLabModel()
    imgs_seged = seg_model.run(imgs_editted_rgb)

    # -------3. (honban)---------

    # encode from png to binary
    imgs_encoded = [encode_img(image) for image in imgs_seged]

    # return binary png image
    return imgs_encoded

    # -------3. (debug)---------

    # save image
    # for i, image in enumerate(imgs_seged):
    #     # print(image.shape)
    #     cv2.imwrite(f"res_img/256-all/{i+1}.png", image)


if __name__ == "__main__":
    main()
