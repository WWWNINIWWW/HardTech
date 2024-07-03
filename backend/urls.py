from django.urls import path
from backend.views import PCList
from backend import views

urlpatterns = [
    path('user/',PCList.as_view()),
    path('media/', views.media_view, name='media'),
    path('media/<str:user>/', views.user_media_view, name='user_media'),
    path('user/<str:user>/', views.UserPCList.as_view(), name='user_pc_list'),
    path('power/<str:user>/', views.PCPowerUpdateView.as_view(), name='update-power')
]