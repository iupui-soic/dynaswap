import numpy as np
from scipy.signal import convolve2d
from DynaSwapApp.services.face_models.face_model import FaceService


class FaceUtils:
    def preprocess(self, image):
        return FaceService().get_input(image)

    def embed(self, image):
        return FaceService().get_feature(image)

    def __signature_extraction(self, feature):
        lvl1 = convolve2d(feature.reshape(32, 16), np.ones(
            (5, 5)) / 25., mode="same", boundary="wrap")
        lvl2 = feature.reshape(32, 16) - lvl1
        signature = np.around(np.average(lvl2, axis=1) * 100.).astype(int) % 9
        return signature

    def __key_generation(self, signature):
        key = np.empty((0,))
        for sig in signature:
            np.random.seed(sig)
            key = np.append(key, np.random.choice(2, 16))
        key = (key * 2) - 1
        return key

    def biocapsule(self, user_feature, rs_feature):
        user_signature = self.__signature_extraction(user_feature)
        user_key = self.__key_generation(user_signature)
        rs_signature = self.__signature_extraction(rs_feature)
        rs_key = self.__key_generation(rs_signature)
        return np.multiply(user_feature, rs_key) + np.multiply(rs_feature, user_key)
