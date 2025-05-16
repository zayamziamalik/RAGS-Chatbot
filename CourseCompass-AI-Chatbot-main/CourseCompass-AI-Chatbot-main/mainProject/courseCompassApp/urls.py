from django.urls import path,include
from . import views

urlpatterns = [
    path('',views.home),
    path('generate_response',views.generate_response,name='generate_response'  ),
]
