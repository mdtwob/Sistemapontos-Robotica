from django.urls import path
from . import views
from django.views.generic import RedirectView

urlpatterns = [
    # ROTAS DE LOGIN/LOGOUT REMOVIDAS DAQUI
    
    # Home (Redireciona para o ponto após o login)
    path('', RedirectView.as_view(pattern_name='tela_ponto'), name='home'),
    
    # Rotas do Sistema
    path('ponto/', views.tela_ponto, name='tela_ponto'),
    path('ponto/bater/', views.bater_ponto, name='bater_ponto'), 
    path('relatorio/', views.relatorio, name='relatorio'),
    path('cadastro/', views.cadastro, name='cadastro'), 
    
    # Rotas de Gerenciamento e Perfil
    path('usuarios/', views.gerenciar_usuarios, name='gerenciar_usuarios'),
    path('usuarios/excluir/<int:user_id>/', views.excluir_usuario, name='excluir_usuario'), 
    
    path('perfil/', views.perfil, name='perfil'), 
    path('perfil/<int:user_id>/', views.perfil, name='editar_perfil_usuario'),
    
    path('relatorio/', views.relatorio, name='relatorio'),
    # NOVO: API de busca de relatório (POST)
    path('api/relatorio/buscar/', views.buscar_relatorio_pontos, name='buscar_relatorio_pontos'),   
    
    path('api/relatorio/buscar/', views.buscar_relatorio_pontos, name='buscar_relatorio_pontos'),
    # NOVO: Rota para gerar o PDF
    path('api/relatorio/pdf/', views.gerar_relatorio_pdf, name='gerar_relatorio_pdf'),
]