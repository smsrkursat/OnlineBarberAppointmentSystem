from app.models.models import User, UserRole

def is_customer(user_id):
    user = User.query.get(user_id)
    if not user:
        return False
    if user.role == UserRole.CUSTOMER:
        return True
    return any(er.extra_role == UserRole.CUSTOMER for er in user.extra_roles)
