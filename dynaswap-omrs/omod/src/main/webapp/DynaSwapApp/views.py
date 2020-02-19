import os
import cv2
import pickle
import base64
import numpy as np
from threading import Thread
from django.utils import timezone
from django.http import JsonResponse
from django.shortcuts import render
from django.templatetags.static import static
from django.views.generic import TemplateView
from django.core.files.base import ContentFile
from DynaSwapApp.models import Roles
from DynaSwapApp.models import Users
from DynaSwapApp.models import UsersRoles
from DynaSwapApp.models import DynaSwapUsers
from DynaSwapApp.services.register import Register
from DynaSwapApp.services.authenticate import Authenticate


class HomePageView(TemplateView):
    def get(self, request, **kwargs):
        return render(request, "index.html")


class RegisterPageView(TemplateView):
    def get(self, request, **kwargs):
        return render(request, "register.html")


class AuthenticatePageView(TemplateView):
    def get(self, request, **kwargs):
        userName = request.GET.get("userName")
        roleId = request.GET.get("roleId")
        return render(request, "authenticate.html", {"userName": userName, "roleId": roleId})


class AcceptedPageView(TemplateView):
    def get(self, request, **kwargs):
        userName = request.GET.get("userName")
        confidence = request.GET.get("confidence")
        roleId = request.GET.get("roleId")
        return render(request, "accepted.html", {"userName": userName, "confidence": confidence, "roleId": roleId})


class RejectedPageView(TemplateView):
    def get(self, request, **kwargs):
        userName = request.GET.get("userName")
        confidence = request.GET.get("confidence")
        roleId = request.GET.get("roleId")
        return render(request, "rejected.html", {"userName": userName, "confidence": confidence, "roleId": roleId})


class GetRolesView(TemplateView):
    def get(self, request, **kwargs):
        roles = []
        for role in Roles.objects.all().only("role", "url"):
            roles.append({"role": role.role, "url": static(role.url)})
        return JsonResponse({"status": "true", "roles": roles})


class RegisterView(TemplateView):
    __reg = Register()

    def update_database(self, user_id, role, bcs):
        # Train classifier using biocapsules
        classifier = self.__reg.register_classifier(user_id, role, bcs)

        # Convert biocapsules and classifier to binary to save in database
        classifier_binary = pickle.dumps(
            classifier, protocol=pickle.HIGHEST_PROTOCOL)
        bcs_binary = pickle.dumps(bcs, protocol=pickle.HIGHEST_PROTOCOL)

        # Save new user into database
        try:
            new_user = DynaSwapUsers(
                dynaswap_user_id=user_id, role=role, bio_capsule=bcs_binary, classifier=classifier_binary)
            new_user.save()
        except Exception:
            raise Exception("Database connection error during registration.")

        print("Registration - Database updated.")
        return

    def post(self, request, **kwargs):
        # Get POST data form
        try:
            # Extract data
            user_name = request.POST.get("userName", "")
            role = request.POST.get("role", "")

            # Check username exists
            user_found = Users.objects.filter(username=user_name)
            if user_found.count() < 1:
                return JsonResponse({"status": "unknown_user", "error": "Username " + user_name + " has not been registered."})

            # Check if already registered
            user_instance = user_found[0]
            user_id = user_instance.user_id
            dynaswap_user = DynaSwapUsers.objects.filter(
                dynaswap_user_id=user_id, role=role)
            if dynaswap_user.count() > 0:
                return JsonResponse({"status": "already_registered", "error": user_name + " already registered as " + role + " role."})

            # Check user_role pair exists
            user_role = UsersRoles.objects.filter(user_id=user_id, role=role)
            if user_role.count() < 1:
                return JsonResponse({"status": "invalid_user_role_combo", "error": user_name + " cannot be registered as " + role + " role."})

            # Extract uploaded images into byte array elements
            images = []
            for key, value in request.POST.items():
                if key[:5] == "image":
                    format, imgstr = value.split(";base64,")
                    ext = format.split("/")[-1]
                    image = ContentFile(base64.b64decode(
                        imgstr), name="temp." + ext)
                    images.append(image)

            # Convert submited images to biocapsules
            bcs = np.empty((0, 514), dtype=object)
            for image in images:
                stream = image.file
                image = cv2.imdecode(np.fromstring(
                    stream.getvalue(), dtype=np.uint8), 1)
                try:
                    bc = self.__reg.register_image(image, user_id, role)
                except Exception as e:
                    return JsonResponse({"status": "detection_error", "error": str(e)})
                bcs = np.vstack([bcs, bc])

            # Update database
            t = Thread(target=self.update_database, args=(user_id, role, bcs))
            t.setDaemon(True)
            t.start()
        except Exception as e:
            return JsonResponse({"status": "error", "error": str(e)})

        return JsonResponse({"status": "true"})


class AuthenticateView(TemplateView):
    __reg = Register()
    __auth = Authenticate()

    def update_database(self, user_found, bc, bcs):
        # Update user bcs
        bcs = np.vstack([bcs, bc])
        bcs_binary = pickle.dumps(bcs, protocol=pickle.HIGHEST_PROTOCOL)
        user_found.bio_capsule = bcs_binary

        # Update user classifier
        classifier = self.__reg.register_classifier(
            user_found.dynaswap_user_id, user_found.role, bcs)
        classifier_binary = pickle.dumps(classifier)
        user_found.classifier = classifier_binary

        # Save updated user into database
        user_found.last_authenticated = timezone.now()
        user_found.save()
        print("Authentication - Database updated")
        return

    def post(self, request, **kwargs):
        # Get POST data form
        try:
            # Extract data
            user_name = request.POST.get("userName", "")
            role = request.POST.get("role", "")

            # Get user
            user_found = Users.objects.filter(username=user_name)
            if user_found.count() < 1:
                return JsonResponse({"status": "authenticate_failed"})
            user_id = user_found[0].user_id

            # Check valid user
            user_found = DynaSwapUsers.objects.filter(
                dynaswap_user_id=user_id, role=role)
            if user_found.count() < 1:
                return JsonResponse({"status": "authenticate_failed"})
            user_found = user_found[0]

            temp_image = request.POST.get("image", "")
            format, imgstr = temp_image.split(";base64,")
            ext = format.split("/")[-1]
            image = ContentFile(base64.b64decode(imgstr), name="temp." + ext)

            # Convert submited images to biocapsules
            stream = image.file
            image = cv2.imdecode(np.fromstring(
                stream.getvalue(), dtype=np.uint8), 1)
            try:
                bc = self.__auth.authenticate_image(image, user_id, role)
            except Exception as e:
                return JsonResponse({"status": "detection_error", "error": str(e)})

            # Get classifier corresponding to username
            classifier = pickle.loads(user_found.classifier)

            # Perform authentication
            classification, prob = self.__auth.authenticate_classifier(
                bc[:-2], classifier)

            # Classification outcome
            if not classification:
                return JsonResponse({"status": "authenticate_failed"})

            # Update user with authentication time, new bc, new classifier
            if prob > 0.70:
                bcs = pickle.loads(user_found.bio_capsule)
                t = Thread(target=self.update_database,
                           args=(user_found, bc, bcs))
                t.setDaemon(True)
                t.start()

            # Update user with authentication time
            else:
                user_found.last_authenticated = timezone.now()
                user_found.save()
        except Exception as e:
            return JsonResponse({"status": "error", "error": str(e)})

        return JsonResponse({"status": "authenticate_success"})


class GetUserRoleView(TemplateView):
    def get(self, request, **kwargs):
        try:
            user_name = request.GET.get("userName")
            role = request.GET.get("role")

            # Check valid user
            user_found = Users.objects.filter(username=user_name)
            if user_found.count() < 1:
                return JsonResponse({"status": "unknown"})
            user_instance = user_found[0]

            # Check valid user/role
            user_role_found = UsersRoles.objects.filter(
                user_id=user_instance.user_id, role=role)
            if user_role_found.count() < 1:
                return JsonResponse({"status": "unknown"})

            dynaswap_user = DynaSwapUsers.objects.filter(
                dynaswap_user_id=user_instance.user_id, role=role)

            # Check not already registered
            if dynaswap_user.count() > 0:
                return JsonResponse({"status": "already_registered"})

            return JsonResponse({"status": "success", "user_id": user_instance.user_id})
        except Exception as e:
            return JsonResponse({"status": "exception", "error": str(e)})
