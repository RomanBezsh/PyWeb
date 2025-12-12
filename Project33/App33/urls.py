from django.urls import path
from . import views

urlpatterns = [
    path('',               views.home,          name='home'         ),
    path('auth/',          views.auth,          name='auth'         ),
    path('test/',          views.test,          name='test'         ),
    path('clonning/',      views.clonning,      name='clonning'     ),
    path('forms/',         views.forms,         name='forms'        ),
    path('form-delivery/', views.form_delivery, name='form_delivery'),
    path('form-styled/',   views.form_styled,   name='form_styled'  ),
    path('hello/',         views.hello,         name='hello'        ),
    path('layouting/',     views.layouting,     name='layouting'    ),
    path('models/',        views.models,        name='models'       ),
    path('params/',        views.params,        name='params'       ),
    path('seed/',          views.seed,          name='seed'         ),
    path('signup/',        views.signup,        name='signup'       ),
    path('statics/',       views.statics,       name='statics'      ),
]

'''
Д.З. Реалізувати у файлі-шаблоні додатковий блок "footer"
який розміщуватиметься у footer-і.
Перенести до нього відомості про "Сторінка завантажена о"
Заповнювати ці дані з контексту при завантаженні.
'''