import os
import cv2
import pickle
import numpy as np
from sklearn.svm import SVC
from DynaSwapApp.services.face_utils import FaceUtils
from DynaSwapApp.models import Roles
from DynaSwap.settings import BASE_DIR


class Register:
    def register_image(self, image, user_id, role):
        face_util = FaceUtils()
        # Preprocess
        try:
            image = face_util.preprocess(image)
        except Exception as e:
            raise ValueError("Multiple or no faces detected in image.")
            print("Multiple or no faces detected in image.")

        # Feature extraction
        user_feature = face_util.embed(image)
        user_feature_flip = face_util.embed(cv2.flip(image, 1))

        # Get RS feature from database
        rs_feature = pickle.loads(Roles.objects.filter(
            role=role)[0].feature)[:-1].astype(float)

        # BioCapsule generation
        bcs = np.empty((2, 514), dtype=object)
        bcs[0] = np.append(face_util.biocapsule(
            user_feature, rs_feature), [user_id, role])
        bcs[1] = np.append(face_util.biocapsule(
            user_feature_flip, rs_feature), [user_id, role])
        return bcs

    def register_classifier(self, user_id, role, bcs):
        # Load dummy features to use as negative examples
        filename = os.path.join(BASE_DIR, "DynaSwapApp",
                                "services", "data", "dummy_biocapsules.npz")
        dummy = np.load(filename, allow_pickle=True)["arr_0"]

        data = np.vstack([bcs, dummy])
        y = np.ones((data.shape[0],))
        roles = data[:, -1]
        ids = data[:, -2].astype(float)

        y[roles != role] = 0
        y[ids != user_id] = 0
        data = data[:, :-2].astype(float)

        classifier = SVC(kernel="rbf", C=1.0, degree=3,
                         gamma="auto", probability=True)
        classifier.fit(data, y)

        return classifier
