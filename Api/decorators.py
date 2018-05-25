from Api.utils import permission_refused, not_authenticated


def seiler_permission(func):
    def _wrapper(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            if hasattr(user, 'seiler'):
                return func(self, request, *args, **kwargs)
            else:
                return permission_refused()
        else:
            return not_authenticated()
    return _wrapper


def userinfo_permission(func):
    def _wrapper(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            if hasattr(user, 'userinfo'):
                return func(self, request, *args, **kwargs)
            else:
                return permission_refused()
        else:
            return not_authenticated()
    return _wrapper
