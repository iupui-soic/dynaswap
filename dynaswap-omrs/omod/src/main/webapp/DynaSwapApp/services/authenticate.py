import cv2
import numpy as np
import os
import pickle
from sklearn.svm import SVC
from DynaSwapApp.services.face_utils import FaceUtils
from DynaSwapApp.services.face_models.MTCNN import MtcnnService
from DynaSwapApp.services.face_models.FNET import FnetService
from DynaSwapApp.models import Roles


class Authenticate:
    def authenticate_image(self, image, user_id, role):
        face_util = FaceUtils()
        # Preprocess
        try:
            image = face_util.align(image)
        except:
            raise ValueError('Multiple or no faces detected in image.')
            print('Multiple or no faces detected in image.')

        # Feature extraction
        feature = face_util.extract(image)

        # Get RS feature from database
        rs_feature = Roles.objects.filter(role=role)[0].feature
        rs_feature = pickle.loads(rs_feature)[0, 0, :-1].astype(float)

        # BioCapsule generation
        bc = face_util.bc_fusion(user_id, feature, role, rs_feature)
        return bc

    def authenticate_classifier(self, bc, classifier):
        prod = classifier.predict_proba(bc.reshape(1, 512))
        if prod[0, 0] >= prod[0, 1]:
            return False, prod[0, 1]
        return True, prod[0, 1]
