
def get_role_status(user):
    if user.role == 'specialist':
        return 'new'
    elif user.role == 'director':
        return 'approved_by_specialist'
    elif user.role == 'chairman':
        return 'sent_to_chairman'
    else:
        return None
