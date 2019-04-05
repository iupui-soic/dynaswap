from DynaSwapApp.services.face_models import facenet
import tensorflow as tf
import numpy as np
import cv2
import os
import asyncio


class FnetService():
    __instance = None

    class __FnetModel:
        def __init__(self):
            self.sess = None
            self.images_placeholder = None
            self.embeddings = None
            self.phase_train_placeholder = None
            self.embedding_size = 0

    def __init__(self):
        if not FnetService.__instance:
            FnetService.__instance = FnetService.__FnetModel()
            self.initialized = True
            loop = asyncio.new_event_loop()
            loop.run_until_complete(self.background())

    def prewhiten(self, x):
        mean = np.mean(x)
        std = np.std(x)
        std_adj = np.maximum(std, 1.0 / np.sqrt(x.size))
        y = np.multiply(np.subtract(x, mean), 1.0 / std_adj)
        return y

    def feature(self, image):
        # Ensure image is color image
        if len(image.shape) != 3:
            raise ValueError("Color image is required for FaceNet feature embedding!")

        # Ensure image is 160x160x3
        if image.shape != (160, 160, 3):
            image = cv2.resize(image, (160, 160))

        # Normalize image
        image = self.prewhiten(image)

        # Put image into input array
        input = np.zeros((1, 160, 160, 3))
        input[0, :, :, :] = image

        # Perform FaceNet feature embedding
        feed_dict = {self.__instance.images_placeholder: input, self.__instance.phase_train_placeholder: False}
        output = self.__instance.sess.run(self.__instance.embeddings, feed_dict=feed_dict)

        return output

    @staticmethod
    async def initFnetModel(self):
        self.__instance.sess = tf.Session()
        # 20180408-102900//20180408-102900.pb 0.9965 VGGFace2 Inception ResNet v1
        dir = os.path.dirname(__file__)
        model_path = os.path.join(dir, '20180408-102900.pb')
        facenet.load_model(model_path)

        # Get input and output tensors
        self.__instance.images_placeholder = tf.get_default_graph().get_tensor_by_name("input:0")
        self.__instance.embeddings = tf.get_default_graph().get_tensor_by_name("embeddings:0")
        self.__instance.phase_train_placeholder = tf.get_default_graph().get_tensor_by_name("phase_train:0")
        self.__instance.embedding_size = self.__instance.embeddings.get_shape()[1]

    @classmethod
    async def background(self):
        asyncio.ensure_future(self.initFnetModel(self))
        return
