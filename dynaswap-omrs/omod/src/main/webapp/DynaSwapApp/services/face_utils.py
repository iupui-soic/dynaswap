import cv2
import numpy as np
from DynaSwapApp.services.face_models.MTCNN import MtcnnService
from DynaSwapApp.services.face_models.FNET import FnetService


class FaceUtils:
    ########## PREPROCESSING #########################
    def align(self, image):
        # Convert image to BGR if grayscale
        if len(image.shape) < 3:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

        # Get RGB version of BGR OpenCV image
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Get face bounding box and landmarks using MTCNN method
        # Face bounding box points [top_left,bottom_right]
        # Face landmark points [eye_right,eye_left,nose,mouth_right,mouth_left]
        face_bb, face_pts = MtcnnService().detect(image_rgb)

        # Get number of faces detected
        nrof_faces = face_bb.shape[0]

        # No faces are detected
        if nrof_faces == 0:
            raise ValueError('No faces detected in user image! (align)')
            print('No faces detected in user image! (align)')

        # Multiple faces are detected
        if nrof_faces > 1:
            raise ValueError('Multiple faces detected in user image! (align)')
            print('Multiple faces detected in user image! (align)')

        # One face is detected
        # Get left and right eye points
        eye_left = (face_pts[1], face_pts[6])
        eye_right = (face_pts[0], face_pts[5])

        eye_center = np.zeros((3,))
        eye_center[0] = (eye_left[0] + eye_right[0]) / 2
        eye_center[1] = (eye_left[1] + eye_right[1]) / 2
        eye_center[2] = 1.

        # Compute angle between eyes
        dY = eye_right[1] - eye_left[1]
        dX = eye_right[0] - eye_left[0]
        angle = np.degrees(np.arctan2(dY, dX)) - 180

        # Get size and center point of image
        (h, w) = image.shape[:2]
        (cX, cY) = (w / 2, h / 2)

        # Get rotation matrix
        M = cv2.getRotationMatrix2D((cX, cY), angle, 1.0)
        cos = np.abs(M[0, 0])
        sin = np.abs(M[0, 1])

        # Get size of image after rotation
        nW = int((h * sin) + (w * cos))
        nH = int((h * cos) + (w * sin))
        M[0, 2] += (nW / 2) - cX
        M[1, 2] += (nH / 2) - cY

        # Perform rotation
        image = cv2.warpAffine(image, M, (nW, nH))

        # Get eye center point after rotation
        eye_center = M @ eye_center

        return self.__crop(image, aligned=True, rot_center=eye_center)

    def __crop(self, image, out_size=160, margin=44, aligned=False, rot_center=None):
        # Convert image to BGR if grayscale
        if len(image.shape) < 3:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

        # Get RGB version of BGR OpenCV image
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Get face bounding box and landmarks using MTCNN method
        # Face bounding box points [top_left,bottom_right]
        bb, pts = MtcnnService().detect(image_rgb)

        # Get number of faces detected
        nrof_faces = bb.shape[0]

        # No faces are detected
        if nrof_faces == 0:
            raise ValueError('No faces detected in user image! (crop)')
            print('No faces detected in user image! (crop)')

        # Multiple faces are detected
        if nrof_faces > 1:
            raise ValueError('Multiple faces detected in user image! (crop)')
            print('Multiple faces detected in user image! (crop)')

        # Format face boudning box
        bb = np.around(bb[0]).astype(int)
        bb[0] = np.maximum(bb[0] - margin / 2, 0)
        bb[1] = np.maximum(bb[1] - margin / 2, 0)
        bb[2] = np.maximum(bb[2] + margin / 2, 0)
        bb[3] = np.maximum(bb[3] + margin / 2, 0)

        face_bb = []
        for i in range(0, 3, 2):
            face_bb.append((bb[i], bb[i + 1]))

        # Get face detection
        face = image[face_bb[0][1]:face_bb[1][1], face_bb[0][0]:face_bb[1][0]]

        # Resize face image
        face = cv2.resize(face, (out_size, out_size))

        # Return detected face
        return face
    ##################################################

    ########## FEATURE EXTRACTION ####################
    def extract(self, image):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        feature = FnetService().feature(image)
        return feature
    ##################################################

    ########## BC GENERATION #########################
    def bc_fusion(self, user_id, user_feature, role, rs_feature):
        user_signature = self.__signature_extraction(user_feature)
        user_key = self.__key_generation(user_signature)

        rs_signature = self.__signature_extraction(rs_feature)
        rs_key = self.__key_generation(rs_signature)

        bc = np.multiply(user_feature, rs_key) + np.multiply(rs_feature, user_key)
        bc = np.append(bc, user_id).astype(object)
        bc = np.append(bc, role)
        bc = np.reshape(bc, (1, 514))
        return bc

    def __signature_extraction(self, feature):
        feature_grid = np.reshape(feature, (32, 16))
        LTP = np.zeros(feature_grid.shape)
        inc = 3
        B_size = np.floor(np.array([3, 3]) / 2).astype(int)
        T_size = np.floor(np.array([5, 5]) / 2).astype(int)
        for r in range(0, feature_grid.shape[0], inc):
            for c in range(0, feature_grid.shape[1], inc):
                # Get T window
                T_r_s = max([0, r - T_size[0]])
                T_r_e = min([feature_grid.shape[0], r + T_size[0]])
                T_c_s = max([0, c - T_size[1]])
                T_c_e = min([feature_grid.shape[1], c + T_size[0]])
                T = feature_grid[T_r_s:T_r_e + 1, T_c_s:T_c_e + 1]

                # Get T window mean
                T_mean = np.mean(T)

                # Get B window
                B_r_s = max([0, r - B_size[0]])
                B_r_e = min([feature_grid.shape[0], r + B_size[0]])
                B_c_s = max([0, c - B_size[1]])
                B_c_e = min([feature_grid.shape[1], c + B_size[0]])
                B = feature_grid[B_r_s:B_r_e + 1, B_c_s:B_c_e + 1]
                LTP[B_r_s:B_r_e + 1, B_c_s:B_c_e + 1] = np.abs(B - T_mean)

        LTP = np.around(np.average(LTP, axis=1) * 100).astype(int)
        return LTP

    def __key_generation(self, signature):
        key = np.zeros((512,))
        idx = 0
        for i, s in enumerate(signature):
            np.random.seed(s)
            for j in range(16):
                key[idx] = np.random.rand()
                idx = idx + 1

        key = np.around(key)
        key = (key * 2) - 1
        return key
    ##################################################
