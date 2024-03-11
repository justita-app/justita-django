from django.http import Http404, HttpRequest


def lawyer_only(func):
    def wrapper(*args, **kwargs):
        request: HttpRequest = args[0]
        if request.user.username == "" or not request.user.is_lawyer:
            raise Http404()
        return func(*args, **kwargs)
    return wrapper
