from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.core.models import Persona, UserProfile, UserRol, Rol, Cliente
from datetime import date

# Ejecutar el comando python manage.py crear_usuarios_prueba

class Command(BaseCommand):
    help = 'Crea usuarios de prueba: superadmin, admin y gonzalo'

    def handle(self, *args, **options):
        # Crear roles si no existen
        self.crear_roles()
        
        # 1. SUPERADMIN
        self.crear_superadmin()
        
        # 2. ADMINS
        self.crear_nuevos_admins()
        
        # 3. CLIENTE (necesito el modelo Cliente para completar)
        self.crear_cliente()
        
        # Resumen
        self.mostrar_credenciales()

    def crear_roles(self):
        """Crea los roles básicos del sistema"""
        roles_data = [
            {'nombre_rol': 'Super Administrador', 'codigo_rol': 'SUPERADMIN', 'descripcion_rol': 'Acceso total al sistema'},
            {'nombre_rol': 'Administrador', 'codigo_rol': 'ADMIN', 'descripcion_rol': 'Gestión del sistema'},
            {'nombre_rol': 'Cliente', 'codigo_rol': 'CLIENTE', 'descripcion_rol': 'Usuario cliente'},
        ]
        
        for rol_data in roles_data:
            Rol.objects.get_or_create(
                codigo_rol=rol_data['codigo_rol'],
                defaults={
                    'nombre_rol': rol_data['nombre_rol'],
                    'descripcion_rol': rol_data['descripcion_rol'],
                    'activo': True
                }
            )
        self.stdout.write(self.style.SUCCESS('✓ Roles creados/verificados'))

    def crear_superadmin(self):
        """Crea el superadministrador"""
        if User.objects.filter(username='superadmin').exists():
            self.stdout.write(self.style.WARNING('⚠ Superadmin ya existe'))
            return

        # 1. Crear Persona
        persona = Persona.objects.create(
            primer_nombre='Super',
            segundo_nombre='Admin',
            apellido_paterno='Sistema',
            apellido_materno='Principal',
            documento_identidad='11111111',
            dv='1',
            mail='superadmin@graficagyg.com',
            cod_tel_pais='+56',
            cod_telefono='9',
            telefono_persona='87654321',
            fecha_nacimiento=date(1980, 1, 1),
            activo=True
        )

        # 2. Crear User de Django
        user = User.objects.create_superuser(
            username='superadmin',
            email='superadmin@graficagyg.com',
            password='Emi05255',
            first_name='Super',
            last_name='Sistema',
            is_staff=True,
            is_superuser=True,
            is_active=True
        )

        # 3. Crear UserProfile
        user_profile = UserProfile.objects.create(
            persona=persona,
            user=user,
            mail_verified=True,
            activo=True
        )

        # 4. Asignar Rol
        rol_superadmin = Rol.objects.get(codigo_rol='SUPERADMIN')
        UserRol.objects.create(
            user_profile=user_profile,
            rol=rol_superadmin,
            activo=True
        )

        self.stdout.write(self.style.SUCCESS('✓ Superadmin creado exitosamente'))

    def crear_nuevos_admins(self):
        """Crea los nuevos administradores solicitados, incluyendo a Gonzalo (si no existe)"""
        
        # Lista de usuarios a crear
        # NOTA: Se ha incluido a Gonzalo en esta lista para consolidar la creación de todos los administradores.
        # Se han agregado RUT y DV ficticios para los nuevos usuarios.
        nuevos_usuarios = [
            {
                'primer_nombre': 'Belén',
                'segundo_nombre': '',
                'apellido_paterno': 'Gutierrez',
                'apellido_materno': '',
                'documento_identidad': '19111111',
                'dv': '1',
                'mail': 'infogerenciagyg@gmail.com',
                'username': 'belen',
                'password': '*GyGFranKlin0326',
                'fecha_nacimiento': date(1990, 1, 1),
                'telefono_persona': '12345678',
            },
            {
                'primer_nombre': 'Roxana',
                'segundo_nombre': '',
                'apellido_paterno': 'Gutierrez',
                'apellido_materno': '',
                'documento_identidad': '18222222',
                'dv': '2',
                'mail': 'susanbarczi@gmail.com',
                'username': 'roxana',
                'password': '*GyGFranKlin0326',
                'fecha_nacimiento': date(1988, 2, 2),
                'telefono_persona': '12345678',
            },
            {
                'primer_nombre': 'Francisco',
                'segundo_nombre': '',
                'apellido_paterno': 'Gutierrez',
                'apellido_materno': '',
                'documento_identidad': '17333333',
                'dv': '3',
                'mail': 'francisco.s.gyg@gmail.com',
                'username': 'francisco',
                'password': '*GyGFranKlin0326',
                'fecha_nacimiento': date(1985, 3, 3),
                'telefono_persona': '12345678',
            },
            {
                'primer_nombre': 'Vendedora',
                'segundo_nombre': '',
                'apellido_paterno': 'Gutierrez',
                'apellido_materno': '',
                'documento_identidad': '16444444',
                'dv': '4',
                'mail': 'yenny.mendoza.gyg@gmail.com',
                'username': 'vendedora',
                'password': '*GyGFranKlin0326',
                'fecha_nacimiento': date(1995, 4, 4),
                'telefono_persona': '12345678',
            },
            {
                'primer_nombre': 'Gonzalo',
                'segundo_nombre': '',
                'apellido_paterno': 'Gutierrez',
                'apellido_materno': '',
                'documento_identidad': '15555555',
                'dv': '5',
                'mail': 'gerenciagonzalo28@gmail.com',
                'username': 'gonzalo',
                'password': '*GyGFranKlin0326',
                'fecha_nacimiento': date(1982, 5, 5),
                'telefono_persona': '12345678',
            },
        ]
        
        # Se ha modificado la lista para usar los correos proporcionados en el mensaje original del usuario
        # y se ha ajustado el campo 'username' para que sea el primer nombre en minúsculas.
        
        for user_data in nuevos_usuarios:
            username = user_data['username']
            
            if User.objects.filter(username=username).exists():
                self.stdout.write(self.style.WARNING(f'⚠ Admin {username} ya existe'))
                continue

            # 1. Crear Persona
            persona = Persona.objects.create(
                primer_nombre=user_data['primer_nombre'],
                segundo_nombre=user_data['segundo_nombre'],
                apellido_paterno=user_data['apellido_paterno'],
                apellido_materno=user_data['apellido_materno'],
                documento_identidad=user_data['documento_identidad'],
                dv=user_data['dv'],
                mail=user_data['mail'],
                cod_tel_pais='+56',
                cod_telefono='9',
                telefono_persona=user_data['telefono_persona'],
                fecha_nacimiento=user_data['fecha_nacimiento'],
                activo=True
            )

            # 2. Crear User de Django
            user = User.objects.create_user(
                username=username,
                email=user_data['mail'],
                password=user_data['password'],
                first_name=user_data['primer_nombre'],
                last_name=user_data['apellido_paterno'], # Usar apellido paterno como last_name
                is_staff=True,
                is_superuser=False,
                is_active=True
            )

            # 3. Crear UserProfile
            user_profile = UserProfile.objects.create(
                persona=persona,
                user=user,
                mail_verified=True,
                activo=True
            )

            # 4. Asignar Rol
            rol_admin = Rol.objects.get(codigo_rol='ADMIN')
            UserRol.objects.create(
                user_profile=user_profile,
                rol=rol_admin,
                activo=True
            )

            self.stdout.write(self.style.SUCCESS(f'✓ Admin {username} creado exitosamente'))
            
        self.stdout.write(self.style.SUCCESS('✓ Todos los nuevos administradores procesados'))

    def crear_cliente(self):
        """Crea el cliente"""
        if User.objects.filter(username='cliente_prueba').exists():
            self.stdout.write(self.style.WARNING('⚠ Cliente cliente_prueba ya existe'))
            return

        # 1. Crear Persona
        persona = Persona.objects.create(
            primer_nombre='Cliente',
            segundo_nombre='',
            apellido_paterno='Prueba',
            apellido_materno='',
            documento_identidad='18765432',
            dv='1',
            mail='cliente.prueba@email.com',
            cod_tel_pais='+56',
            cod_telefono='9',
            telefono_persona='12345678',
            cod_tel_pais_wp='+56',
            cod_tel_wp='9',
            whatsapp_persona='12345678',
            fecha_nacimiento=date(1992, 3, 20),
            activo=True
        )

        # 2. Crear User de Django
        user = User.objects.create_user(
            username='cliente_prueba',
            email='cliente.prueba@email.com',
            password='*GyGFranKlin0326',
            first_name='Cliente',
            last_name='Prueba',
            is_staff=False,
            is_superuser=False,
            is_active=True
        )

        # 3. Crear UserProfile
        user_profile = UserProfile.objects.create(
            persona=persona,
            user=user,
            mail_verified=True,
            activo=True
        )

        # 4. Asignar Rol
        rol_cliente = Rol.objects.get(codigo_rol='CLIENTE')
        UserRol.objects.create(
            user_profile=user_profile,
            rol=rol_cliente,
            activo=True
        )

        # 5. Crear Cliente (corregido)
        Cliente.objects.create(
            user_profile=user_profile,  # ✓ Nombre correcto del campo
            nombre_cliente='Cliente Prueba',  # ✓ Nombre completo
            telefono='+56912345678'  # ✓ Campo requerido y único
            # ultima_interaccion se setea automáticamente con auto_now=True
        )
        
        self.stdout.write(self.style.SUCCESS('✓ Cliente gonzalo creado exitosamente'))

    def mostrar_credenciales(self):
        """Muestra las credenciales de acceso"""
        self.stdout.write(self.style.SUCCESS('\n=== CREDENCIALES DE ACCESO ==='))
        self.stdout.write('Superadmin:')
        self.stdout.write('  Usuario: superadmin')
        self.stdout.write('  Password: Emi05255')
        self.stdout.write('  Email: superadmin@graficagyg.com')
        self.stdout.write('')
        self.stdout.write('Administradores:')
        self.stdout.write('  Usuario: belen, roxana, francisco, vendedora, gonzalo')
        self.stdout.write('  Password: *GyGFranKlin0326 (para todos)')
        self.stdout.write('  Emails: infogerenciagyg@gmail.com, susanbarczi@gmail.com, francisco.s.gyg@gmail.com, yenny.mendoza.gyg@gmail.com, gerenciagonzalo28@gmail.com')
        self.stdout.write('')
        self.stdout.write('Cliente:')
        self.stdout.write('  Usuario: cliente_pruebas')
        self.stdout.write('  Password: *GyGFranKlin0326')
        self.stdout.write('  Email: cliente.prueba@email.com')  