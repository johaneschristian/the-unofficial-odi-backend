from django.urls import path
from .views import (
    serve_register_company,
    serve_register_assessor,
    generate_assessor_one_time_code
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register-company/', serve_register_company),
    path('register-assessor/', serve_register_assessor),
    path('generate-code/', generate_assessor_one_time_code),
]
