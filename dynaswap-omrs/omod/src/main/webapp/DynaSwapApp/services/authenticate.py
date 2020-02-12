import pickle
import numpy as np
from DynaSwapApp.services.face_utils import FaceUtils
from DynaSwapApp.models import Roles


class Authenticate:
    def authenticate_image(self, image, user_id, role):
        face_util = FaceUtils()
        # Preprocess
        try:
            image = face_util.preprocess(image)
        except Exception as e:
            raise ValueError("Multiple or no faces detected in image.")
            print("Multiple or no faces detected in image.")

        # Feature extraction
        query_feature = face_util.embed(image)

        # Get RS feature from database
        rs_feature = pickle.loads(Roles.objects.filter(
            role=role)[0].feature)[:-1].astype(float)

        # BioCapsule generation
        bc = np.append(face_util.biocapsule(
            query_feature, rs_feature).astype(object), [user_id, role])
        return bc

    def authenticate_classifier(self, bc, classifier):
        prod = classifier.predict_proba(bc.reshape(1, 512))
        if prod[0, 0] >= prod[0, 1]:
            return False, prod[0, 1]
        return True, prod[0, 1]
