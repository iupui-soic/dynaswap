import cv2
import numpy as np
import os
import pickle
from sklearn.svm import SVC
from DynaSwapApp.services.face_utils import FaceUtils
from DynaSwapApp.services.face_models.MTCNN import MtcnnService
from DynaSwapApp.services.face_models.FNET import FnetService
from DynaSwapApp.models import Roles
from DynaSwap.settings import BASE_DIR


class Register:
    def register_image(self, image, user_id, role):
        face_util = FaceUtils()
        # Preprocess
        try:
            image = face_util.align(image)
        except:
            raise ValueError('Multiple or no faces detected in image.')
            print('Multiple or no faces detected in image.')

        # Feature extraction
        feature = face_util.extract(image)
        feature_flip = face_util.extract(cv2.flip(image, 1))

        # Get RS feature from database
        rs_feature = Roles.objects.filter(role=role)[0].feature
        rs_feature = pickle.loads(rs_feature)[0, 0, :-1].astype(float)

        # BioCapsule generation
        bcs = np.empty((0, 514))
        bc = face_util.bc_fusion(user_id, feature, role, rs_feature)
        bc_flip = face_util.bc_fusion(user_id, feature_flip, role, rs_feature)
        bcs = np.vstack([bcs, bc])
        bcs = np.vstack([bcs, bc_flip])

        return bcs

    def register_classifier(self, user_id, role, bcs):
        # Load dummy features to use as negative examples
        filename = os.path.join(BASE_DIR, 'DynaSwapApp', 'services', 'data', 'dummy_bc.npz')
        dummy = np.load(filename)['arr_0']

        data = np.vstack([bcs, dummy])
        y = np.ones((data.shape[0]))
        roles = data[:, -1]
        ids = data[:, -2].astype(float)

        y[roles != role] = 0
        y[ids != user_id] = 0
        data = data[:, :-2].astype(float)

        classifier = SVC(kernel='rbf', C=1.0, degree=3, gamma='auto', probability=True)
        classifier.fit(data, y)

        return classifier
