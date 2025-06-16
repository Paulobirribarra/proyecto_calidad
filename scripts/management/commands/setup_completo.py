from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Configura todo el entorno del Colegio Clara Brincefield con datos de ejemplo'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Elimina todos los datos existentes antes de crear nuevos',
        )
        parser.add_argument(
            '--skip-usuarios',
            action='store_true',
            help='Omite la creación de usuarios',
        )
        parser.add_argument(
            '--skip-salas',
            action='store_true',
            help='Omite la creación de salas',
        )
        parser.add_argument(
            '--skip-reservas',
            action='store_true',
            help='Omite la creación de reservas',
        )
        parser.add_argument(
            '--skip-reseñas',
            action='store_true',
            help='Omite la creación de reseñas',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS("\n🏫 CONFIGURACIÓN COMPLETA DEL COLEGIO CLARA BRINCEFIELD 🏫")
        )
        self.stdout.write("="*70)
        
        reset_flag = options.get('reset', False)
        
        try:
            # 1. Configurar salas
            if not options.get('skip_salas', False):
                self.stdout.write("\n📚 PASO 1/4: Configurando salas del colegio...")
                if reset_flag:
                    call_command('setup_colegio', '--delete-existing')
                else:
                    call_command('setup_colegio')
                self.stdout.write(self.style.SUCCESS("✅ Salas configuradas correctamente"))
            
            # 2. Configurar usuarios
            if not options.get('skip_usuarios', False):
                self.stdout.write("\n👥 PASO 2/4: Configurando usuarios...")
                if reset_flag:
                    call_command('setup_usuarios', '--reset')
                else:
                    call_command('setup_usuarios')
                self.stdout.write(self.style.SUCCESS("✅ Usuarios configurados correctamente"))
            
            # 3. Crear reservas de ejemplo
            if not options.get('skip_reservas', False):
                self.stdout.write("\n📅 PASO 3/4: Creando reservas de ejemplo...")
                if reset_flag:
                    call_command('setup_reservas', '--cantidad', '25', '--reset')
                else:
                    call_command('setup_reservas', '--cantidad', '25')
                self.stdout.write(self.style.SUCCESS("✅ Reservas creadas correctamente"))
            
            # 4. Crear reseñas de ejemplo
            if not options.get('skip_reseñas', False):
                self.stdout.write("\n⭐ PASO 4/4: Creando reseñas de ejemplo...")
                if reset_flag:
                    call_command('setup_reseñas', '--cantidad', '20', '--reset')
                else:
                    call_command('setup_reseñas', '--cantidad', '20')
                self.stdout.write(self.style.SUCCESS("✅ Reseñas creadas correctamente"))
            
            # Resumen final
            self.stdout.write("\n" + "="*70)
            self.stdout.write(self.style.SUCCESS("🎉 ¡CONFIGURACIÓN COMPLETADA EXITOSAMENTE! 🎉"))
            self.stdout.write("="*70)
            
            self.stdout.write("\n📋 CREDENCIALES DE ACCESO:")
            self.stdout.write("   🔐 Administrador: admin / demo123")
            self.stdout.write("   👨‍🏫 Profesores: profesor1, profesor2, profesor3 / demo123")
            self.stdout.write("   🎓 Estudiantes: estudiante1, estudiante2, estudiante3 / demo123")
            self.stdout.write("   🔧 Personal: tecnico1, administrativo1, soporte1 / demo123")
            
            self.stdout.write("\n🚀 El sistema está listo para usar:")
            self.stdout.write("   • Salas del Colegio Clara Brincefield configuradas")
            self.stdout.write("   • Usuarios con diferentes roles creados")
            self.stdout.write("   • Reservas de ejemplo distribuidas en el tiempo")
            self.stdout.write("   • Reseñas realistas para las salas")
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"\n❌ Error durante la configuración: {e}")
            )
            self.stdout.write("💡 Puedes ejecutar comandos individuales para diagnosticar:")
            self.stdout.write("   python manage.py setup_colegio --delete-existing")
            self.stdout.write("   python manage.py setup_usuarios --reset")
            self.stdout.write("   python manage.py setup_reservas --reset")
            self.stdout.write("   python manage.py setup_reseñas --reset")
