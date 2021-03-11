from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model



class Command(BaseCommand):
    help = 'Migration of management data for initializing project '

    def handle(self, *args, **options):
        User = get_user_model()
        if User.objects.count() == 0:
            #management.call_command('loaddata', 'accounts', verbosity=1)
            #management.call_command('loaddata', 'billing', verbosity=1)
            admin = User.objects.create_superuser(
                        username='admin', email="admin@mayafin.in",
                        password='google@123')
            admin.is_active = True
            admin.is_admin = True
            admin.is_staff = True
            admin.save()

            self.stdout.write(self.style.SUCCESS('Created superuser and loaded module fixtures.'))
            self.stdout.write(self.style.SUCCESS('Project initialization completed :)'))

        else:
            self.stdout.write(self.style.SUCCESS('Project is already initialized :)'))
