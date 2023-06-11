from django.shortcuts import render_to_response


def bad_request(request):
    response = render_to_response("base/400.html")
    response.status_code = 400

    return response


def page_not_found(request, exception):
    response = render_to_response("base/404.html")
    response.status_code = 404

    return response


def permission_denied(request):
    response = render_to_response("base/403.html")
    response.status_code = 403

    return response


def server_error(request, exception):
    response = render_to_response("base/500.html")
    response.status_code = 500

    return response
