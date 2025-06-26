from app.models.models import User, UserRole

def is_owner(user_id):
    user = User.query.get(user_id)
    if not user:
        return False
    if user.role == UserRole.SALON_OWNER:
        return True
    return any(er.extra_role == UserRole.SALON_OWNER for er in user.extra_roles)
