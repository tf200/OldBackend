from django.shortcuts import get_object_or_404
from ninja import NinjaAPI
from ninja.security import HttpBearer
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed, InvalidToken

from ai.api import router as ai_router
from assessments.api import router as assessment_router
from authentication.models import CustomUser
from client.api import router as contract_router
from system.api import router as system_router


class TokenAuth(HttpBearer):
    def authenticate(self, request, token):
        try:
            jwt = JWTTokenUserAuthentication()
            validated_token = jwt.get_validated_token(token)
            jwt_user = jwt.get_user(validated_token)
            user = get_object_or_404(CustomUser, id=jwt_user.id)
            request.user = user
            return user
        except (InvalidToken, AuthenticationFailed):
            pass


api = NinjaAPI(auth=TokenAuth())

api.add_router("/system", system_router, tags=["system"])
api.add_router("/assessments", assessment_router, tags=["assessments"])
api.add_router("/ai", ai_router, tags=["ai"])
api.add_router("/contracts", contract_router, tags=["contract"])
