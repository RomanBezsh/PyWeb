import binascii
from django.http import HttpResponse, HttpResponseNotAllowed, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.template import loader
from .forms.demo_form import DemoForm
from .forms.styled_form import StyledForm
from .forms.delivery_form import DeliveryForm
from .forms.signup_form import SignupForm
from datetime import datetime
from .helper import * 
from .models import *
import base64
import uuid
# технічно представлення - це функції, які приймають
# запит (request) та формують відповідь (response)


def test(request):
    # Перевірити наявність заголовку "Authorization", якщо немає - статус 401
    authHeader = request.headers.get("Authorization")
    if not authHeader:
        return HttpResponse("Missing 'Authorization' header", status=401)

    authScheme = "Bearer "
    print('test endpoint Authorization header:', authHeader)
    if not authHeader.startswith(authScheme):
        return HttpResponse("Invalid 'Authorization' scheme", status=401)

    token = authHeader[len(authScheme):]
    
    if not token:
        return HttpResponse("Missing token", status=401)

    try:
        access = Access.objects.get(token=token)
    except Access.DoesNotExist:
        return HttpResponse("Invalid token", status=401)

    return HttpResponse("Token removed", status=200)

def auth(request) :
    authHeader = request.headers.get("Authorization")
    if not authHeader :
        return HttpResponse("Missing 'Authorization' header", status=401)
    authScheme = "Basic "
    if not authHeader.startswith(authScheme) :
        return HttpResponse("Invalid 'Authorization' scheme", status=401)
    credentials = authHeader[len(authScheme):]
    if len(credentials) < 4 :
        return HttpResponse("Credentials too short", status=401)
    try :
        user_pass = base64.b64decode(credentials).decode()
    except Exception as err :
        return HttpResponse("Credentials decode error: " + str(err), status=401)
    parts = user_pass.split(':', 1)
    if len(parts) != 2 :
        return HttpResponse("User-pass decode error", status=401)
    login, password = parts
    try :
        access = Access.objects.get(login=login)    
    except Access.DoesNotExist :
        return HttpResponse("Authorization rejected", status=401)
    _salt = access.salt
    _dk = dk(password, _salt)
    if _dk != access.dk :
        return HttpResponse("Authorization rejected.", status=401)
    access.token = str(uuid.uuid4())
    access.token_dt = datetime.now()
    access.save()
    return HttpResponse(access.token, status=200)


def clonning(request) :
    template = loader.get_template('clonning.html')
    return HttpResponse( template.render() )


def form_delivery(request) :
    template = loader.get_template('form_delivery.html')
    if request.method == 'GET' :
        context = {
            'form': DeliveryForm()
        }
    elif request.method == 'POST' :
        form = DeliveryForm(request.POST)
        context = {
            'form': form
        }
    return HttpResponse( template.render(context=context, request=request) )


def form_styled(request) :
    template = loader.get_template('form_styled.html')
    if request.method == 'GET' :
        context = {
            'form': StyledForm()
        }
    elif request.method == 'POST' :
        form = StyledForm(request.POST)
        context = {
            'form': form
        }
    return HttpResponse( template.render(context=context, request=request) )


def forms(request) :
    if request.method == 'GET' :
        template = loader.get_template('forms.html')
        context = {
            'form': DemoForm()
        }
    elif request.method == 'POST' :
        form = DemoForm(request.POST)
        context = {
            'form': form
        }
        template = loader.get_template('form_ok.html' if form.is_valid() else 'forms.html')
    else :
        return HttpResponseNotAllowed()
    
    return HttpResponse( template.render(context=context, request=request) )


def hello(request) :
    return HttpResponse("Hello, world!")


def home(request) :
    template = loader.get_template('home.html')
    context = {
        'x': 10,
        'y': 20,
        'page_title': 'Домашня',
        'page_header': 'Розробка вебдодатків з використанням Python',
        'now': datetime.now().strftime("%H:%M:%S %d.%m.%Y")
    }
    return HttpResponse( template.render(context, request) )


def layouting(request) :
    template = loader.get_template('layouting.html')
    return HttpResponse( template.render() )


def models(request) :
    template = loader.get_template('models.html')
    return HttpResponse( template.render(request=request) )


def params(request) :    
    context = {
        'params': str(request.GET),
        'user': request.GET.get('user', 'Немає даних'),
        'q': request.GET.get('q', 'Немає даних'),
    }
    about = request.GET.get('about', None)
    if about == 'GET' :
        context['about_get'] = " (метод не має тіла і вживається як запит на читання)"
    elif about == 'POST' :
        context['about_post'] = " (метод може мати тіло і вживається як запит на створення)"
    '''Д.З. Створити посилання-підказки для НТТР-методів PUT, PATCH, DELETE
    (аналогічно створеним на занятті для методів GET, POST).
    До звіту додавати скріншоти'''
    template = loader.get_template('params.html')
    return HttpResponse( template.render(context, request) )


@csrf_exempt
def seed(request) :
    if request.method == 'PATCH' :
        res = {
            "guest": "",
            "admin-role": "",
            "admin-user": "",
            "admin-access": "",
            "guest-user": "",
            "guest-access": ""
        }
        try :
            guest = Role.objects.get(name="Self registered")
        except Role.DoesNotExist :
            guest = Role()
            guest.name = "Self registered"
            res["guest"] = "created"
        else :
            res["guest"] = "updated"
        guest.create_level = guest.read_level = guest.update_level = guest.delete_level = 0
        guest.save()

        try :
            admin = Role.objects.get(name="Root Administrator")    
        except Role.DoesNotExist :
            admin = Role()
            admin.name = "Root Administrator"
            res["admin-role"] = "created"
        else : 
            res["admin-role"] = "updated"
        admin.create_level = admin.read_level = admin.update_level = admin.delete_level = 1
        admin.save()
        
        
        try :
            admin = User.objects.get(first_name="Default", last_name='Administrator')    
        except User.DoesNotExist :
            admin = User()
            admin.first_name = "Default"
            admin.last_name  = 'Administrator'
            admin.email      = 'admin@change.me'
            admin.phone      = '0000000000'
            admin.save()
            res["admin-user"] = "created"
        else : 
            res["admin-user"] = "ignored"

            
        try :
            admin_access = Access.objects.get(user=admin)    
        except Access.DoesNotExist :
            admin_access = Access()
            res["admin-access"] = "created"
        else : 
            res["admin-access"] = "updated"
        _salt = salt()
        _dk = dk('root', _salt)
        admin_access.user  = admin
        admin_access.role  = Role.objects.get(name="Root Administrator")
        admin_access.login = 'admin'
        admin_access.salt  = _salt
        admin_access.dk    = _dk
        admin_access.save()
        # Д.З. Розширити метод сідування: додати тестового користувача
        # з гостьовою роллю. Якщо немає - створювати, якщо є - оновлювати
        # логін та пароль

        try:
            guest_user = User.objects.get(first_name="Guest", last_name="User")
        except User.DoesNotExist:
            guest_user = User()
            guest_user.first_name = "Guest"
            guest_user.last_name = "User"
            guest_user.email = 'guest@gmail.com'
            guest_user.phone = '0000000001'
            guest_user.save()
            res["guest-user"] = "created"
        else:
            guest_user.email = guest_user.email or 'guest@gmail.com'
            guest_user.phone = guest_user.phone or '0000000001'
            guest_user.save()
            res["guest-user"] = "updated"

        try:
            guest_access = Access.objects.get(user=guest_user)
        except Access.DoesNotExist:
            guest_access = Access()
            res["guest-access"] = "created"
        else:
            res["guest-access"] = "updated"

        _salt_g = salt()
        _dk_g = dk('guest', _salt_g)
        guest_access.user = guest_user
        guest_access.role = Role.objects.get(name="Self registered")
        guest_access.login = 'guest'
        guest_access.salt = _salt_g
        guest_access.dk = _dk_g
        guest_access.save()
        return JsonResponse(res)
    
    else :
        template = loader.get_template('seed.html')
        return HttpResponse( template.render() )


def signup(request) :
    template = loader.get_template('signup.html')
    if request.method == 'GET' :
        context = {
            'form': SignupForm()
        }
    elif request.method == 'POST' :
        form = SignupForm(request.POST)
        context = {
            'form': form,
            'is_ok': form.is_valid()
        }
        if form.is_valid() :
            form_data = form.cleaned_data
            _salt = salt()
            _dk = dk(form_data['password'], _salt)
            
            user = User()
            user.first_name = form_data['first_name']
            user.last_name  = form_data['last_name']
            user.email      = form_data['email']
            user.phone      = form_data['phone']
            user.birthdate  = form_data['birthdate']
            user.save()

            user_access = Access()
            user_access.user  = user
            user_access.role  = Role.objects.get(name="Self registered")
            user_access.login = form_data['login']
            user_access.salt  = _salt
            user_access.dk    = _dk
            user_access.save()

            context['user'] = user
            context['user_access'] = user_access

    # context['salt'] = salt()    
    # context['dk'] = dk("123", "456")    
    return HttpResponse( template.render(request=request, context=context) )


def statics(request) :
    template = loader.get_template('statics.html')
    return HttpResponse( template.render() )
