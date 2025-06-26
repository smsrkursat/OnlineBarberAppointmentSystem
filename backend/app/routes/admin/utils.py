from app.models.models import User, UserRole

def is_admin(user_id):
    user = User.query.get(user_id)
    if not user:
        return False
    if user.role == UserRole.ADMIN:
        return True
    return any(er.extra_role == UserRole.ADMIN for er in user.extra_roles)
