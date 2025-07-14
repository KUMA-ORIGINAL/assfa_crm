
def permission_callback(request):
    if request.user.is_superuser:
        return True
    return False


def permission_callback_my_requests(request):
    if request.user.role in ('specialist', 'director', 'chairman'):
        return True
    return False

