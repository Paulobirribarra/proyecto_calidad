from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction, IntegrityError
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Crea usuarios de demostración para el Colegio Clara Brincefield'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Elimina usuarios existentes antes de crear nuevos',
        )

    def handle(self, *args, **options):
        self.stdout.write("🏫 Configurando usuarios para Colegio Clara Brincefield...")
        
        if options['reset']:
            usuarios_existentes = User.objects.count()
            if usuarios_existentes > 0:
                User.objects.all().delete()
                self.stdout.write(f"🗑️ Eliminados {usuarios_existentes} usuarios existentes")
        
        usuarios_creados = 0

        # ADMINISTRADOR (Solo 1)
        self.stdout.write("\n🔧 Creando Administrador...")
        try:
            admin_user = User.objects.create_user(
                username='admin',
                email='admin@clarabrincefield.edu',
                password='demo123',
                first_name='Clara',
                last_name='Brincefield',
                role='admin',
                is_staff=True,
                is_superuser=True,
                is_active=True,
                email_notifications=True,
                phone_number=f"+569{random.randint(10000000, 99999999)}"
            )
            usuarios_creados += 1
            self.stdout.write(f"   ✅ admin - {admin_user.email} (Admin/Staff/Superuser)")
        except IntegrityError:
            self.stdout.write(f"   ⚠️ Usuario 'admin' ya existe")

        # PROFESORES (3 usuarios)
        self.stdout.write("\n👨‍🏫 Creando Profesores...")
        profesores_data = [
            ('profesor1', 'Dr. Juan', 'Pérez', 'profesor1@clarabrincefield.edu'),
            ('profesor2', 'Dra. María', 'González', 'profesor2@clarabrincefield.edu'),
            ('profesor3', 'Prof. Carlos', 'Rodríguez', 'profesor3@clarabrincefield.edu'),
        ]
        
        for username, first_name, last_name, email in profesores_data:
            try:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password='demo123',
                    first_name=first_name,
                    last_name=last_name,
                    role='profesor',
                    is_active=True,
                    email_notifications=True,
                    phone_number=f"+569{random.randint(10000000, 99999999)}"
                )
                usuarios_creados += 1
                self.stdout.write(f"   ✅ {username} - {email}")
            except IntegrityError:
                self.stdout.write(f"   ⚠️ Usuario '{username}' ya existe")

        # ESTUDIANTES (3 usuarios)
        self.stdout.write("\n🎓 Creando Estudiantes...")
        estudiantes_data = [
            ('estudiante1', 'Ana', 'Martínez', 'estudiante1@estudiantes.clarabrincefield.edu'),
            ('estudiante2', 'Pedro', 'López', 'estudiante2@estudiantes.clarabrincefield.edu'),
            ('estudiante3', 'Sofía', 'Torres', 'estudiante3@estudiantes.clarabrincefield.edu'),
        ]
        
        for username, first_name, last_name, email in estudiantes_data:
            try:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password='demo123',
                    first_name=first_name,
                    last_name=last_name,
                    role='estudiante',
                    is_active=True,
                    email_notifications=True,
                    phone_number=f"+569{random.randint(10000000, 99999999)}"
                )
                usuarios_creados += 1
                self.stdout.write(f"   ✅ {username} - {email}")
            except IntegrityError:
                self.stdout.write(f"   ⚠️ Usuario '{username}' ya existe")

        # PERSONAL TÉCNICO/ADMINISTRATIVO (3 usuarios)
        self.stdout.write("\n🔧 Creando Personal Técnico/Administrativo...")
        tecnicos_data = [
            ('tecnico1', 'Luis', 'Vargas', 'tecnico1@clarabrincefield.edu', 'tecnico'),
            ('administrativo1', 'Carmen', 'Silva', 'admin1@clarabrincefield.edu', 'administrativo'),
            ('soporte1', 'Miguel', 'Hernández', 'soporte1@clarabrincefield.edu', 'soporte'),
        ]
        
        for username, first_name, last_name, email, role in tecnicos_data:
            try:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password='demo123',
                    first_name=first_name,
                    last_name=last_name,
                    role=role,
                    is_active=True,
                    email_notifications=True,
                    phone_number=f"+569{random.randint(10000000, 99999999)}"
                )
                usuarios_creados += 1
                self.stdout.write(f"   ✅ {username} - {email} ({role})")
            except IntegrityError:
                self.stdout.write(f"   ⚠️ Usuario '{username}' ya existe")

        # RESUMEN
        self.stdout.write("\n" + "="*50)
        self.stdout.write(f"✅ USUARIOS CREADOS: {usuarios_creados}")
        self.stdout.write("="*50)
        self.stdout.write("\n📋 CREDENCIALES DE ACCESO:")
        self.stdout.write("   🔑 Todos los usuarios: contraseña 'demo123'")
        self.stdout.write("   🔐 Administrador: admin / demo123")
        self.stdout.write("   👨‍🏫 Profesores: profesor1, profesor2, profesor3 / demo123")
        self.stdout.write("   🎓 Estudiantes: estudiante1, estudiante2, estudiante3 / demo123")
        self.stdout.write("   🔧 Personal: tecnico1, administrativo1, soporte1 / demo123")
