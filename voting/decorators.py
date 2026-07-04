from django.shortcuts import redirect


def student_login_required(view_func):

    def wrapper(request, *args, **kwargs):

        if "student_id" not in request.session:
            return redirect("student_login")

        return view_func(request, *args, **kwargs)

    return wrapper