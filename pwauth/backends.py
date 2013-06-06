from pwauth import pwauth

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend

import logging

def get_user_groups(username):
    import grp
    return [g.gr_name for g in grp.getgrall() if username in g.gr_mem]

def intersect(a,b):
    for x in a:
        if x in b:
            return True
    return False

class PWAuthBackend(ModelBackend):
    def authenticate(self, username=None, password=None):
        logging.debug('Trying to auth "%s"' % (username))
        if pwauth(username, password):

            d = getattr(settings,'PWAUTH', {})

            # User has to be in a valid group to 
            valid_groups = d.get('VALID_GROUPS', [])
            all_staff = d.get('ALL_STAFF', False)
            superusers = d.get('SUPERUSERS', [])
            superusers_groups = d.get('SUPERUSERS_GROUPS', [])
            staff_groups = d.get('STAFF_GROUPS', [])
            django_group_id = d.get('DJANGO_GROUP_ID', None)
            in_staff_group = False
            in_superuser_group = False

            user_groups = []

            # check if user is in valid system groups
            if valid_groups or superusers_groups or staff_groups:
                user_groups = get_user_groups(username)

            if valid_groups:
                if not intersect(valid_groups, user_groups):
                    logging.debug('User not in a valid group (PWAUTH:VALID_GROUPS)')
                    return None

            if intersect(user_groups, superusers_groups):
                in_superuser_group = True

            if intersect(user_groups, staff_groups):
                in_staff_group = True

            try:
                user = User.objects.get(username=username)
            except:
                user = User(username=username, password='not stored here')
                user.set_unusable_password()
#                if django_group_id:
#                    user.groups.add(django_group_id)

            if username in superusers or in_superuser_group:
                user.is_superuser = True
            else:
                user.is_superuser = False

            if all_staff or in_staff_group:
                user.is_staff = True
            else:
                user.is_staff = False

            user.save()

            if django_group_id:
                user.groups.add(django_group_id)
                user.save()

            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
