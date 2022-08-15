from django.shortcuts import render
from os import path


def page_not_found(request, exception):
    return render(
        request,
        path.join('core', '404.html'),
        {'path': request.path},
        status=404
    )


def permission_denied_view(request, exception):
    return render(
        request,
        path.join('core', '403.html'),
        {'path': request.path},
        status=403
    )


def internal_server_error_view(request):
    return render(
        request,
        path.join('core', '500.html'),
        status=500
    )
