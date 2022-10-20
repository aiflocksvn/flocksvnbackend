from django.db.models.signals import post_save

from .models import SystemUser
from ..dashboard.models import IdentityVerification



def create_id_verification_transaction(sender, instance: SystemUser, **kwargs):

    if instance.role == SystemUser.CLIENT_ROLE and (not getattr(instance, 'identity', None)):
        IdentityVerification.objects.create(user=instance)


post_save.connect(create_id_verification_transaction, sender=SystemUser)
