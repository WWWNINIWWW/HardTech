from django.urls import path
from backend.views import PCList
from backend import views

urlpatterns = [
    path('user/',PCList.as_view()),
    path('media/', views.media_view, name='media'),
    path('media/<str:user>/', views.user_media_view, name='user_media'),
    path('user/<str:user>/', views.UserPCList.as_view(), name='user_pc_list'),
    
    
    path('fans/', views.PCFanStatusListView.as_view(), name='fan-status-list'),
    
    path('fans/change-mode/', views.PCFanUpdateByJSONView.as_view(), name='fan-change-mode'),
    
    # GET: Visualizar status do usuário específico
    # PUT: Atualizar o mode_fan do usuário (e colocar 'update' em True)
    path('fans/<str:user>/', views.PCFanDetailAndUpdateView.as_view(), name='fan-detail-update'),
    
    # PUT: Atualizar diretamente a flag de 'update' (ex: voltar para False)
    path('fans/<str:user>/update/', views.PCUpdateFlagView.as_view(), name='fan-update-flag'),
    
    
]