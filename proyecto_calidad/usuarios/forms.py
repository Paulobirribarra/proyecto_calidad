"""
Formularios para la gestión de usuarios.

Este módulo contiene formularios para registro, login,
edición de perfil y gestión de usuarios.

REQ-012: Formularios de autenticación y perfil
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
import re

from .models import CustomUser


class LoginForm(forms.Form):
    """
    Formulario de login personalizado.
    
    Incluye validaciones adicionales y
    mejor experiencia de usuario.
    """
    
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre de usuario o email',
            'autofocus': True
        })
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña'
        })
    )
    
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    def clean_username(self):
        """Validar formato del username."""
        username = self.cleaned_data.get('username')
        
        if username:
            # Permitir login con email o username
            if '@' in username:
                # Es un email, verificar que existe un usuario con ese email
                try:
                    user = CustomUser.objects.get(email=username)
                    return user.username  # Retornar el username real
                except CustomUser.DoesNotExist:
                    raise ValidationError("No existe un usuario con ese email.")
            else:
                # Es un username, verificar que existe
                if not CustomUser.objects.filter(username=username).exists():
                    raise ValidationError("No existe un usuario con ese nombre.")
        
        return username
    
    def clean(self):
        """Validación cruzada del formulario."""
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        
        if username and password:
            # Verificar credenciales
            user = authenticate(username=username, password=password)
            if user is None:
                raise ValidationError("Credenciales inválidas.")
            
            if not user.is_active:
                raise ValidationError("Esta cuenta está desactivada.")
        
        return cleaned_data


class CustomUserCreationForm(UserCreationForm):
    """
    Formulario de registro personalizado.
    
    Extiende UserCreationForm con campos adicionales
    y validaciones mejoradas.
    """
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'correo@ejemplo.com'
        })
    )
    
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre'
        })
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Apellido'
        })
    )
    
    phone_number = forms.CharField(
        max_length=15,
        required=False,        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+56 949 377 625'
        })
    )
    
    terms_accepted = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        error_messages={
            'required': 'Debes aceptar los términos y condiciones.'
        }
    )
    
    email_notifications = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    class Meta:
        model = CustomUser
        fields = (
            'username', 'first_name', 'last_name', 
            'email', 'phone_number', 'email_notifications',
            'password1', 'password2', 'terms_accepted'
        )
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'nombre_usuario'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Personalizar widgets de contraseñas
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Contraseña'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirmar contraseña'
        })
        
        # Personalizar mensajes de ayuda
        self.fields['username'].help_text = "Solo letras, números y @/./+/-/_ caracteres."
        self.fields['password1'].help_text = "Mínimo 8 caracteres con letras y números."
    
    def clean_email(self):
        """Validar email único."""
        email = self.cleaned_data.get('email')
        
        if email:
            if CustomUser.objects.filter(email=email).exists():
                raise ValidationError("Ya existe un usuario con este email.")
        
        return email
    
    def clean_username(self):
        """Validar username con reglas adicionales."""
        username = self.cleaned_data.get('username')
        
        if username:
            # Verificar que no contenga espacios
            if ' ' in username:
                raise ValidationError("El nombre de usuario no puede contener espacios.")
            
            # Verificar longitud mínima
            if len(username) < 3:
                raise ValidationError("El nombre de usuario debe tener al menos 3 caracteres.")
            
            # Verificar que no sea solo números
            if username.isdigit():
                raise ValidationError("El nombre de usuario no puede ser solo números.")
        
        return username
    
    def clean_phone_number(self):
        """Validar formato de teléfono."""
        phone = self.cleaned_data.get('phone_number')
        
        if phone:
            # Remover espacios y caracteres especiales para validación
            phone_clean = re.sub(r'[^\d+]', '', phone)
            
            # Validar formato básico
            if not re.match(r'^\+?[\d\s\-\(\)]{10,15}$', phone):
                raise ValidationError(
                    "Formato de teléfono inválido. Ejemplo: +52 555 123 4567"
                )
        
        return phone
    
    def clean_password1(self):
        """Validar fortaleza de contraseña."""
        password1 = self.cleaned_data.get('password1')
        
        if password1:
            # Validar longitud mínima
            if len(password1) < 8:
                raise ValidationError("La contraseña debe tener al menos 8 caracteres.")
            
            # Validar que contenga letras y números
            if not re.search(r'[A-Za-z]', password1):
                raise ValidationError("La contraseña debe contener al menos una letra.")
            
            if not re.search(r'\d', password1):
                raise ValidationError("La contraseña debe contener al menos un número.")
            
            # Validar que no sea muy común
            common_passwords = ['12345678', 'password', 'qwerty123', '123456789']
            if password1.lower() in common_passwords:
                raise ValidationError("Esta contraseña es muy común. Elige una más segura.")
        
        return password1
    
    def save(self, commit=True):
        """Guardar usuario con campos adicionales."""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone_number = self.cleaned_data.get('phone_number', '')
        user.terms_accepted = self.cleaned_data['terms_accepted']
        user.email_notifications = self.cleaned_data.get('email_notifications', True)
        
        if commit:
            user.save()
        
        return user


class ProfileForm(forms.ModelForm):
    """
    Formulario para editar perfil de usuario.
    
    Permite editar información personal del usuario
    sin modificar credenciales sensibles.
    """
    
    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'last_name', 'email', 
            'phone_number', 'email_notifications'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apellido'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@ejemplo.com'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+569 49377625'
            }),
            'email_notifications': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Hacer email obligatorio
        self.fields['email'].required = True
        
        # Agregar ayuda contextual
        self.fields['email_notifications'].help_text = (
            "Recibir notificaciones sobre reservas y recordatorios"
        )
    
    def clean_email(self):
        """Validar email único (excluyendo el usuario actual)."""
        email = self.cleaned_data.get('email')
        
        if email:
            # Verificar si existe otro usuario con este email
            existing_user = CustomUser.objects.filter(email=email).exclude(pk=self.instance.pk)
            if existing_user.exists():
                raise ValidationError("Ya existe otro usuario con este email.")
        return email
    
    def clean_phone_number(self):
        """Validar formato de teléfono."""
        phone = self.cleaned_data.get('phone_number')
        
        if phone:
            # Validar formato básico
            if not re.match(r'^\+?[\d\s\-\(\)]{10,15}$', phone):
                raise ValidationError(
                    "Formato de teléfono inválido. Ejemplo: +569 49377625"
                )
        
        return phone


class CustomUserChangeForm(UserChangeForm):
    """
    Formulario para administradores para editar usuarios.
    
    Extiende UserChangeForm con campos personalizados
    y validaciones para administradores.
    """
    
    class Meta:
        model = CustomUser
        fields = [
            'username', 'first_name', 'last_name', 'email',
            'phone_number', 'role', 'is_active', 'is_staff',
            'email_notifications'
        ]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'email_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Remover el campo de contraseña del formulario de cambio
        if 'password' in self.fields:
            del self.fields['password']
        
        # Agregar ayuda contextual
        self.fields['role'].help_text = "Rol del usuario en el sistema"
        self.fields['is_staff'].help_text = "Permite acceso al panel de administración"
        self.fields['is_active'].help_text = "Desactivar en lugar de eliminar usuarios"