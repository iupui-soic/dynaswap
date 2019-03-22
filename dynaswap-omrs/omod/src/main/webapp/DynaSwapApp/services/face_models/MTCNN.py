from DynaSwapApp.services.face_models import detect_face
import tensorflow as tf
import numpy as np
import asyncio


class MtcnnService():
    __instance = None

    class __MtcnnModel:
        def __init__(self):
            self.pnet = None
            self.rnet = None
            self.onet = None
            self.minsize = 0
            self.threshold = []
            self.factor = 0

    def __init__(self):
        if not MtcnnService.__instance:
            MtcnnService.__instance = MtcnnService.__MtcnnModel()
            self.initialized = True
            loop = asyncio.new_event_loop()
            loop.run_until_complete(self.background())

    def detect(self, image):
        bounding_boxes, facial_pts = detect_face.detect_face(image, self.__instance.minsize, self.__instance.pnet, self.__instance.rnet, self.__instance.onet, self.__instance.threshold, self.__instance.factor)
        return bounding_boxes, facial_pts

    @staticmethod
    async def initMtcnnModel(self):
        sess = tf.Session()
        self.__instance.pnet, self.__instance.rnet, self.__instance.onet = detect_face.create_mtcnn(sess, None)
        # minimum size of face
        self.__instance.minsize = 100
        # three steps's threshold
        self.__instance.threshold = [0.6, 0.7, 0.7]
        # scale factor
        self.__instance.factor = 0.709

    @classmethod
    async def background(self):
        asyncio.ensure_future(self.initMtcnnModel(self))
        return
