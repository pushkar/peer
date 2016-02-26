from student.models import *

def check_session(request):
    if not 'user' in request.session:
        request.session['user'] = ""
        request.session['usertype'] = ""

    if not request.session['user']:
        return False
    return True

def get_global():
    globals = Global.objects.all()
    data = {}
    for g in globals:
        data[g.key] = g.value
    return data
