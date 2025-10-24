# labpoint_project/urls.py

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views 
from django.conf import settings # NOVO IMPORT: Importa as configurações
from django.conf.urls.static import static # NOVO IMPORT: Para servir arquivos estáticos/mídia

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('login/', auth_views.LoginView.as_view(template_name='ponto_app/index.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/login/'), name='logout'), 
    
    path('', include('django.contrib.auth.urls')), 
    path('', include('ponto_app.urls')), 
]

# NOVO: Adiciona URLs de Mídia (SÓ FUNCIONA EM AMBIENTE DE DESENVOLVIMENTO!)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)