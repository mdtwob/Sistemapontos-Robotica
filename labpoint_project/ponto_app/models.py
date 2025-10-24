from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Criação de um Perfil customizado para adicionar o CPF e o Nível de Acesso
class Perfil(models.Model):
    NIVEIS_ACESSO = [
        ('ADMIN', 'Administrador'),
        ('PROFESSOR', 'Professor Responsável'),
        ('ESTAGIARIO', 'Estagiário'),
        ('ALUNO', 'Aluno/Usuário do Laboratório'),
    ]
    foto_perfil = models.ImageField(
        default='profile_pics/default.png', 
        upload_to='profile_pics', 
        blank=True
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cpf = models.CharField(max_length=11, unique=True, verbose_name="CPF (apenas números)")
    nivel_acesso = models.CharField(max_length=10, choices=NIVEIS_ACESSO, default='ALUNO')

    def __str__(self):
        return f'{self.user.username} - {self.nivel_acesso}'

# Modelo para o registro de Ponto (Entrada/Saída)
class RegistroPonto(models.Model):
    TIPO_PONTO = [
        ('ENTRADA', 'Entrada'),
        ('SAIDA', 'Saída'),
    ]
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    tipo_ponto = models.CharField(max_length=7, choices=TIPO_PONTO)
    data_hora = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.usuario.username} - {self.tipo_ponto} em {self.data_hora.strftime("%Y-%m-%d %H:%M")}'

    class Meta:
        ordering = ['-data_hora'] # Padrão: Registros mais recentes primeiro