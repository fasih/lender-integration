from django.core import management
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model



class Command(BaseCommand):
    help = 'Migration of management data for initializing project '

    def handle(self, *args, **options):
        User = get_user_model()

        if User.objects.count() == 0:
            management.call_command('loaddata', 'initproject', verbosity=1)
            self.stdout.write(self.style.SUCCESS('Created superuser and loaded module fixtures.'))
            self.stdout.write(self.style.SUCCESS('Project initialization completed :)'))
        else:
            self.stdout.write(self.style.SUCCESS('Project is already initialized :)'))
