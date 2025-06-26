from app.models.models import User, UserRole

def is_barber(user_id):
    user = User.query.get(user_id)
    if not user:
        return False
    if user.role == UserRole.BARBER:
        return True
    return any(er.extra_role == UserRole.BARBER for er in user.extra_roles)
