def user_can_authenticate(user):
    """
    Reject users with is_active=False. Custom user models that don't have
    that attribute are allowed.
    """
    is_active = getattr(user, 'is_active', None)
    is_verified = getattr(user, 'is_verified', None)
    return True if is_active and is_verified else False
