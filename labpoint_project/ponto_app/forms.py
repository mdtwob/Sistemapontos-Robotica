# ponto_app/forms.py

from django import forms
from django.contrib.auth.models import User
from .models import Perfil

# Formulário para editar os campos do modelo User (Nome, Email)
class UserEditForm(forms.ModelForm):
    # Adicionamos 'username' para fins de exibição, mas o Django cuida da edição.
    username = forms.CharField(max_length=150, disabled=True, required=False) 

    class Meta:
        model = User
        fields = ['first_name', 'email'] # Campos que vamos permitir editar

# Formulário para editar os campos do modelo Perfil (CPF, Nível de Acesso)
class PerfilEditForm(forms.ModelForm):
    # CPF é desabilitado, pois é uma chave de identificação única.
    cpf = forms.CharField(max_length=11, disabled=True, required=False)

    class Meta:
        model = Perfil
        fields = ['cpf', 'nivel_acesso', 'foto_perfil'] # NOVO CAMPO AQUI!