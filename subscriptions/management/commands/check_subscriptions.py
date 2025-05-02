from django.core.management.base import BaseCommand
from stock.models import Profile
from django.utils.timezone import now

class Command(BaseCommand):
    help = 'Check user subscriptions and suspend expired accounts'

    def handle(self, *args, **kwargs):
        profiles = Profile.objects.filter(account_status='Active', subscription_end__lt=now())
        for profile in profiles:
            profile.account_status = 'Suspended'
            profile.save()
            self.stdout.write(f'Suspended: {profile.user.username}')
