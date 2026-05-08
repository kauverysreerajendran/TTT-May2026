from adminportal.services import get_user_allowed_module_names, is_admin_user


def user_permissions(request):
    """Add user permission context to all templates.
    """
    if request.user.is_authenticated:
        return {
            'is_admin': is_admin_user(request.user),
            'allowed_modules': get_user_allowed_module_names(request.user),
        }

    return {
        'is_admin': False,
        'allowed_modules': [],
    }