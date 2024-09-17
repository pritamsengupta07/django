from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login_user, name="login"),
    path("logout/", views.logout_user, name="logout"),
    path("registration/", views.registration_user, name="registration"),
    path("otp", views.otp_code, name="otp"),
    path('chat',views.chatbot,name='chat')
] 
# + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
