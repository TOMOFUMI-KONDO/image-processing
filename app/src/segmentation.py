import os
import pickle
import cv2
import numpy as np
import tensorflow as tf


class DeepLabModel:
    """Class of deeplearning model for segmentation."""

    INPUT_TENSOR_NAME = "dummyname/ImageTensor:0"
    OUTPUT_TENSOR_NAME = "dummyname/SemanticPredictions:0"
    INPUT_SIZE = 256
    FROZEN_GRAPH_NAME = "frozen_inference_graph"

    # OPTIMIZE: tarファイルの中身もとから出しておけるならそうする
    def __init__(self):
        """Creates and loads pretrained deeplab model"""

        # tensorflowのwarningを消す
        os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

        # GPU 対応
        config = tf.ConfigProto()
        config.gpu_options.allow_growth = True
        tf.keras.backend.set_session(tf.Session(config=config))

        self.graph = tf.Graph()

        graph_def = None

        with open("model/graph_def.pickle", "rb") as f:
            graph_def = pickle.load(f)

        if graph_def is None:
            raise RuntimeError("Cannot find inference graph in tar archive")

        with self.graph.as_default():
            tf.import_graph_def(graph_def, name="dummyname")

        self.sess = tf.compat.v1.Session(graph=self.graph)

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

        # 深層学習モデルを使用してセグメンテーションの処理を実行
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

        # 各画像について、seg_mapをもとに人以外の領域を透過させる
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

    for i, img in enumerate(img_seg_li):
        # img_rgba = cv2.cvtColor(img, cv2.COLOR_RGB2BGRA)

        # # 人以外の部分を透過
        # img_rgba[:, :, 3] = 0
        # img_rgba[:, :, 3][seg_map == 15] = 255
        cv2.imwrite(f"res_img/256-{i}.png", img)


if __name__ == "__main__":
    main()
