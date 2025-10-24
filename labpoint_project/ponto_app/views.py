from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages 
from django.db import IntegrityError 
from django.db.models import Max
from django.utils import timezone
from datetime import datetime, timedelta, date 
from django.contrib.auth.models import User
import json
import io

# Imports do ReportLab (para o PDF)
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO 

# Imports Locais (certifique-se de que o forms.py existe!)
from .models import Perfil, RegistroPonto
from .forms import UserEditForm, PerfilEditForm


# =================================================================
# === TESTES DE PERMISSÃO (DEFINIÇÃO ÚNICA) ===
# =================================================================
def is_admin(user):
    return user.is_authenticated and hasattr(user, 'perfil') and user.perfil.nivel_acesso == 'ADMIN'

def can_manage_users(user):
    return user.is_authenticated and hasattr(user, 'perfil') and user.perfil.nivel_acesso in ['ADMIN', 'PROFESSOR', 'ESTAGIARIO']


# =================================================================
# 1. PONTO PÚBLICO (NÃO REQUER LOGIN)
# =================================================================

def tela_ponto(request):
    """Renderiza a tela principal de bater ponto."""
    return render(request, 'ponto_app/ponto.html')


@require_http_methods(["POST"])
def bater_ponto(request):
    """Lógica de batida de ponto via CPF (PÚBLICA)."""
    try:
        data = json.loads(request.body)
        cpf = data.get('cpf', '').strip()

        if not cpf or not cpf.isdigit() or len(cpf) != 11:
            return JsonResponse({'success': False, 'message': 'CPF inválido (formato).'}, status=400)

        # 1. Busca o usuário pelo CPF
        try:
            perfil = Perfil.objects.select_related('user').get(cpf=cpf)
            usuario = perfil.user
        except Perfil.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Usuário não cadastrado.'}, status=404)

        # 2. Determina o Tipo de Ponto (Entrada ou Saída)
        hoje = timezone.localdate()
        ultimo_ponto = RegistroPonto.objects.filter(usuario=usuario, data_hora__date=hoje).order_by('-data_hora').first()

        tipo_ponto = 'ENTRADA'
        if ultimo_ponto and ultimo_ponto.tipo_ponto == 'ENTRADA':
            tipo_ponto = 'SAIDA'
        
        # 3. Registra o Ponto
        novo_registro = RegistroPonto.objects.create(
            usuario=usuario,
            tipo_ponto=tipo_ponto,
            data_hora=timezone.now()
        )

        return JsonResponse({
            'success': True,
            'message': f'{usuario.get_full_name() or usuario.username}, ponto registrado como {tipo_ponto} às {novo_registro.data_hora.strftime("%H:%M")}.',
            'tipo': tipo_ponto
        })

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Requisição JSON inválida.'}, status=400)
    except Exception as e:
        # Imprime o erro no terminal para debug
        print(f"ERRO CRÍTICO NA VIEW BATER_PONTO: {e}") 
        return JsonResponse({'success': False, 'message': f'Erro interno do servidor. Detalhes: {str(e)}'}, status=500)


# =================================================================
# 2. VIEWS DE GERENCIAMENTO (REQUEREM LOGIN)
# =================================================================

# 2.1 CADASTRO
@login_required
@user_passes_test(can_manage_users)
def cadastro(request):
    perfil_logado = request.user.perfil
    context = {}

    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        email = request.POST.get('email')
        cpf = request.POST.get('cpf')
        password = request.POST.get('password')
        
        if perfil_logado.nivel_acesso == 'ADMIN':
            nivel_acesso = request.POST.get('nivel_acesso', 'ALUNO') 
        else:
            nivel_acesso = 'ALUNO'

        try:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Erro: Nome de usuário já existe. Escolha outro.')
                return render(request, 'ponto_app/cadastro.html', context)
            if Perfil.objects.filter(cpf=cpf).exists():
                 messages.error(request, 'Erro: CPF já cadastrado no sistema.')
                 return render(request, 'ponto_app/cadastro.html', context)
            
            user = User.objects.create_user(
                username=username, email=email, password=password, first_name=first_name, last_name=''
            )
            
            Perfil.objects.create(
                user=user, cpf=cpf, nivel_acesso=nivel_acesso
            )
            
            messages.success(request, f'Usuário "{first_name}" e Perfil criados com sucesso! Nível: {nivel_acesso}')
            return redirect('gerenciar_usuarios') 

        except IntegrityError:
            messages.error(request, 'Erro: Nome de usuário ou CPF já cadastrado (Erro de banco).')
        except Exception as e:
            print(f"ERRO CRÍTICO NO CADASTRO: {e}")
            messages.error(request, f'Erro inesperado ao cadastrar usuário. Verifique se a senha é forte o suficiente. Detalhe: {e}')
        
    return render(request, 'ponto_app/cadastro.html', context)


# 2.2 LISTAGEM DE USUÁRIOS
@login_required
@user_passes_test(can_manage_users)
def gerenciar_usuarios(request):
    perfil_logado = request.user.perfil
    filtro_nivel = request.GET.get('nivel', 'ALL') 
    
    if perfil_logado.nivel_acesso == 'ADMIN':
        usuarios_query = Perfil.objects.exclude(user=request.user).select_related('user').order_by('nivel_acesso', 'user__first_name')
    else:
        usuarios_query = Perfil.objects.filter(nivel_acesso='ALUNO').select_related('user').order_by('user__first_name')

    if perfil_logado.nivel_acesso == 'ADMIN' and filtro_nivel != 'ALL':
        usuarios_query = usuarios_query.filter(nivel_acesso=filtro_nivel)
        
    context = {
        'usuarios': usuarios_query,
        'is_admin': perfil_logado.nivel_acesso == 'ADMIN',
        'current_filter': filtro_nivel,
        'niveis_acesso': [('ALL', 'Todos'), ('ALUNO', 'Alunos'), ('ESTAGIARIO', 'Estagiários'), ('PROFESSOR', 'Professores')] 
    }
    return render(request, 'ponto_app/gerenciar_usuarios.html', context)


# 2.3 EXCLUSÃO (API)
@require_http_methods(["POST"])
@login_required
@user_passes_test(is_admin)
def excluir_usuario(request, user_id):
    try:
        user_to_delete = User.objects.get(pk=user_id)
        
        if user_to_delete == request.user or (hasattr(user_to_delete, 'perfil') and user_to_delete.perfil.nivel_acesso == 'ADMIN'):
             return JsonResponse({'success': False, 'message': 'Ação proibida: Não é permitido excluir um Administrador ou sua própria conta por esta interface.'}, status=403)
        
        user_to_delete.delete()
        return JsonResponse({'success': True, 'message': 'Usuário excluído com sucesso.'})
    
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Usuário não encontrado.'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Erro ao excluir: {str(e)}'}, status=500)


# 2.4 EDIÇÃO DE PERFIL
@login_required
def perfil(request, user_id=None): 
    
    # 1. Determina o alvo
    if user_id:
        if not request.user.perfil.nivel_acesso == 'ADMIN':
             messages.error(request, "Você não tem permissão para editar outros usuários.")
             return redirect('perfil') 
        target_user = get_object_or_404(User, pk=user_id)
    else:
        target_user = request.user

    target_perfil = get_object_or_404(Perfil, user=target_user)


    # 2. Processa o Formulário (POST)
    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=target_user)
        perfil_form = PerfilEditForm(request.POST, request.FILES, instance=target_perfil)
        
        if not request.user.perfil.nivel_acesso == 'ADMIN':
            del perfil_form.fields['nivel_acesso']
            
        if user_form.is_valid() and perfil_form.is_valid():
            
            user_form.save()
            perfil_form.save() 
            
            messages.success(request, f'Perfil de "{target_user.username}" atualizado com sucesso!')
            
            if user_id:
                return redirect('gerenciar_usuarios')
            else:
                return redirect('perfil') 
            
        else:
            messages.error(request, 'Erro ao salvar o formulário. Verifique os campos e o arquivo de imagem.')

    # 3. Carrega o Formulário (GET)
    else:
        user_form = UserEditForm(instance=target_user)
        perfil_form = PerfilEditForm(instance=target_perfil)
        
        if not request.user.perfil.nivel_acesso == 'ADMIN':
             perfil_form.fields['nivel_acesso'].disabled = True

    context = {
        'target_user': target_user,
        'target_perfil': target_perfil,
        'user_form': user_form,
        'perfil_form': perfil_form,
        'is_editing_other': user_id is not None,
        'is_admin': request.user.perfil.nivel_acesso == 'ADMIN',
    }
    return render(request, 'ponto_app/perfil.html', context)


# =================================================================
# 3. VIEWS DE RELATÓRIO (REQUEREM LOGIN)
# =================================================================

# 3.1 PÁGINA DE RELATÓRIO
@login_required
def relatorio(request):
    return render(request, 'ponto_app/relatorio.html')


# 3.2 BUSCA RELATÓRIO (API)
@login_required
@require_http_methods(["POST"])
def buscar_relatorio_pontos(request):
    """Busca dados de ponto baseados em filtros de data/usuário e retorna JSON."""
    try:
        data = json.loads(request.body)
        
        filtro_tipo = data.get('tipo', 'dia')
        cpf = data.get('cpf', '').strip()
        data_inicio_str = data.get('data_inicio')
        
        qs = RegistroPonto.objects.all().select_related('usuario', 'usuario__perfil')
        
        if cpf:
            perfil_alvo = Perfil.objects.get(cpf=cpf)
            qs = qs.filter(usuario=perfil_alvo.user)

        if data_inicio_str:
            data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').date()
            data_fim = data_inicio
            
            if filtro_tipo == 'semana':
                data_inicio -= timedelta(days=data_inicio.weekday() + 1)
                data_fim = data_inicio + timedelta(days=6)
            elif filtro_tipo == 'mes':
                data_inicio = data_inicio.replace(day=1)
                data_fim = (data_inicio.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
            elif filtro_tipo == 'anual':
                data_inicio = data_inicio.replace(month=1, day=1)
                data_fim = data_inicio.replace(month=12, day=31)
            
            qs = qs.filter(data_hora__date__gte=data_inicio, data_hora__date__lte=data_fim)

        pontos = qs.order_by('data_hora').values(
            'tipo_ponto', 'data_hora', 'usuario__first_name', 'usuario__perfil__cpf', 'usuario__perfil__nivel_acesso'
        )
        
        relatorio_dados = [
            {
                'nome': p['usuario__first_name'] or p['usuario__perfil__cpf'],
                'cpf': p['usuario__perfil__cpf'],
                'nivel': p['usuario__perfil__nivel_acesso'],
                'tipo': p['tipo_ponto'],
                'data': timezone.localtime(p['data_hora']).strftime('%Y-%m-%d'),
                'hora': timezone.localtime(p['data_hora']).strftime('%H:%M:%S'),
            } for p in pontos
        ]

        return JsonResponse({
            'success': True, 
            'dados': relatorio_dados,
            'periodo': {
                'inicio': data_inicio.strftime('%Y-%m-%d'),
                'fim': data_fim.strftime('%Y-%m-%d'),
                'filtro': filtro_tipo,
            }
        })

    except Perfil.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'CPF não encontrado.'}, status=404)
    except Exception as e:
        print(f"Erro ao gerar relatório: {e}")
        return JsonResponse({'success': False, 'message': f'Erro interno do servidor: {str(e)}'}, status=500)


# 3.3 GERAÇÃO DE PDF
@login_required
@require_http_methods(["POST"])
def gerar_relatorio_pdf(request):
    """Gera o relatório em PDF usando ReportLab."""
    try:
        # Lida com dados vindos de formulário POST ou JSON direto
        if 'json_data' in request.POST:
            data = json.loads(request.POST.get('json_data'))
        else:
            data = json.loads(request.body)
            
        # --- LÓGICA DE FILTRAGEM (Repetição segura) ---
        filtro_tipo = data.get('tipo', 'dia')
        cpf = data.get('cpf', '').strip()
        data_inicio_str = data.get('data_inicio')
        
        data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').date()
        data_fim = data_inicio
        
        if filtro_tipo == 'semana':
            data_inicio -= timedelta(days=data_inicio.weekday() + 1) 
            data_fim = data_inicio + timedelta(days=6)
        elif filtro_tipo == 'mes':
            data_inicio = data_inicio.replace(day=1)
            data_fim = (data_inicio.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        elif filtro_tipo == 'anual':
            data_inicio = data_inicio.replace(month=1, day=1)
            data_fim = data_inicio.replace(month=12, day=31)
            
        qs = RegistroPonto.objects.filter(data_hora__date__gte=data_inicio, data_hora__date__lte=data_fim).select_related('usuario', 'usuario__perfil')
        
        if cpf:
            perfil_alvo = Perfil.objects.get(cpf=cpf)
            qs = qs.filter(usuario=perfil_alvo.user)

        pontos = qs.order_by('data_hora').all()
        # --- FIM DA LÓGICA DE FILTRAGEM ---

        # 1. Configurar o Documento
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=30, bottomMargin=30, leftMargin=30, rightMargin=30)
        elements = []
        styles = getSampleStyleSheet()
        
        # 2. Título e Info do Período
        titulo = f"RELATÓRIO DE PONTO - LABROBO POINT"
        if cpf and pontos:
            titulo += f" (Usuário: {pontos.first().usuario.get_full_name() or pontos.first().usuario.username})"
        elif cpf:
            titulo += " (Usuário Não Encontrado)"
            
        elements.append(Paragraph(titulo, styles['h1']))
        elements.append(Paragraph(f"Período: {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}", styles['h3']))
        elements.append(Paragraph("<br/>", styles['Normal']))

        # 3. Dados da Tabela
        data_table = [
            ["Data", "Hora", "Nome", "Nível", "CPF", "Tipo"]
        ]
        
        for ponto in pontos:
            data_table.append([
                timezone.localtime(ponto.data_hora).strftime('%d/%m/%Y'),
                timezone.localtime(ponto.data_hora).strftime('%H:%M:%S'),
                ponto.usuario.get_full_name() or ponto.usuario.username,
                ponto.usuario.perfil.nivel_acesso,
                ponto.usuario.perfil.cpf,
                ponto.tipo_ponto
            ])
            
        table = Table(data_table)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.red), 
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white), 
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        elements.append(table)

        # 4. Constrói o PDF e Retorna
        doc.build(elements)
        
        response = HttpResponse(content_type='application/pdf')
        filename = f"Relatorio_Ponto_{data_inicio.strftime('%Y%m%d')}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response.write(buffer.getvalue())
        buffer.close()
        
        return response

    except Perfil.DoesNotExist:
        return HttpResponse("Usuário não encontrado.", status=404)
    except Exception as e:
        print(f"Erro ao gerar PDF: {e}")
        return HttpResponse(f"Erro interno ao gerar PDF: {str(e)}", status=500)