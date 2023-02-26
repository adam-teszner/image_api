from img_api.models import CustUser, Tier
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Creates Basic,Premium,Enterpriese User-Tiers and corresponding users'

    def handle(self, *args, **kwargs):

        # Creates superuser
        sup = User.objects.create_superuser(username='admin', password='admin123')
        self.stdout.write(f'superuser "{sup.username}" was created')

        # Tiers params
        tiers = {
            'basic': {
                'name': 'basic',
                'options': {
                    'small': 200
                },
                'original_link': False,
                'bin_img_exp_link': None,
                'list_details': False
            },
            'premium': {
                'name': 'premium',
                'options': {
                    'small': 200,
                    'medium': 400
                },
                'original_link': True,
                'bin_img_exp_link': None,
                'list_details': False
            },
            'enterprise': {
                'name': 'enterprise',
                'options': {
                    'small': 200,
                    'medium': 400
                },
                'original_link': True,
                'bin_img_exp_link': 300,
                'list_details': False
            },
        }



        # Creates users/tier/custuser and connects them together
        def create_user_tier(name, tier_params):
            
            cred = {
                'username': name,
                'password': name+'123'
            }

            u = User.objects.create_user(**cred)
            t = Tier(**tier_params)
            t.save()
            c = CustUser(
                account_type=t,
                user=u
            )
            c.save()
            self.stdout.write(f'User "{u.username}" was created')


        for name in tiers.keys():
            params = tiers.get(name)
            create_user_tier(name, params)

        self.stdout.write(f'DONE')