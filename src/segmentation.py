"""
https://colab.research.google.com/github/tensorflow/models/blob/master/research/deeplab/deeplab_demo.ipynb#scrollTo=Y7iErVUps7mh
のデモを参考に、セグメンテーションする

生成されたマスク画像をモルフォロジー変換してきれいに
"""

import os
import tarfile
import cv2
import numpy as np
import tensorflow as tf

# tensorflowのwarningを消す
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"


class DeepLabModel:
    """Class of deeplearning model for segmentation."""

    INPUT_TENSOR_NAME = "ImageTensor:0"
    OUTPUT_TENSOR_NAME = "SemanticPredictions:0"
    INPUT_SIZE = 256
    FROZEN_GRAPH_NAME = "frozen_inference_graph"

    # OPTIMIZE: tarファイルの中身もとから出しておけるならそうする
    def __init__(self):
        """Creates and loads pretrained deeplab model"""
        self.graph = tf.Graph()

        self.MODEL_PATH = "model/deeplabv3_pascal_train_aug_2018_01_04.tar.gz"

        graph_def = None
        # Extract frozen graph from tar archive.
        tar_file = tarfile.open(self.MODEL_PATH)
        for tar_info in tar_file.getmembers():
            if self.FROZEN_GRAPH_NAME in os.path.basename(tar_info.name):
                file_handle = tar_file.extractfile(tar_info)
                graph_def = tf.GraphDef.FromString(file_handle.read())
                break

        tar_file.close()

        if graph_def is None:
            raise RuntimeError("Cannot find inference graph in tar archive")

        with self.graph.as_default():
            tf.import_graph_def(graph_def, name="")

        self.sess = tf.Session(graph=self.graph)

    def run(self, images):
        """Runs inference on a batch of images.

        Args:
            images: List of opencv RGB images. All images must be same sized.
        Return:
            resized_image: RGB image resized from original input image.
            seg_map: Segmentation map of 'resized_image'.
        """
        height = images[0].shape[0]
        width = images[0].shape[1]
        resize_ratio = 1.0 * self.INPUT_SIZE / max(width, height)
        target_size = (int(resize_ratio * width), int(resize_ratio * height))

        print("Segmentation Start!!")
        return_li = []
        for image in images:
            resized_image = cv2.resize(
                image, target_size, interpolation=cv2.INTER_CUBIC
            )
            batch_seg_map = self.sess.run(
                self.OUTPUT_TENSOR_NAME,
                feed_dict={self.INPUT_TENSOR_NAME: [np.asarray(resized_image)]},
            )
            seg_map = batch_seg_map[0]
            return_li.append((resized_image, seg_map))
        print("Segmentation Finish!!")

        # return return_li

        img_li = []
        for i, (img, seg_map) in enumerate(return_li):
            img_rgba = cv2.cvtColor(img, cv2.COLOR_RGB2BGRA)

            # personとして判別された面積が全体に対してしきい値以下のときは、画像全体を返す
            THRESH = 1.0 / 10.0
            person_percent = np.count_nonzero(seg_map == 15) / (
                img.shape[0] * img.shape[1]
            )
            print(f"person_percentage-{i}:", person_percent)
            if person_percent > THRESH:
                # 人以外の部分を透過
                img_rgba[:, :, 3] = 0
                img_rgba[:, :, 3][seg_map == 15] = 255
                img_li.append(img_rgba)
            else:
                img_rgba[:, :, 3] = 255
                img_li.append(img_rgba)

            # cv2.imwrite(f"res_img/256-{i}.png", img_rgba)
        return img_li


def main():
    MODEL = DeepLabModel()
    print("Model loaded successfully!")

    IMAGE_NUM = 2

    # load images
    images = []
    for i in range(IMAGE_NUM):
        img = cv2.imread(f"img/crop{i+1}.png")
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
        images.append(img_rgb)

    img_seg_li = MODEL.run(images)

    for i, (img, seg_map) in enumerate(img_seg_li):
        img_rgba = cv2.cvtColor(img, cv2.COLOR_RGB2BGRA)

        # モルフォロジー変換
        # kernel = np.ones((3, 3), np.uint8)
        # mask = (seg_map == 15).astype(np.uint8)
        # mask_closing = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        # 人以外の部分を透過
        img_rgba[:, :, 3] = 0
        img_rgba[:, :, 3][seg_map == 15] = 255
        cv2.imwrite(f"res_img/256-{i}.png", img_rgba)


if __name__ == "__main__":
    main()
