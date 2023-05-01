from django.urls import path

from .views import CompView, TesteView

urlpatterns = [
    path('comp/sicro/<str:estado>/<int:ano>/<int:mes>/<str:des>/<str:pk>', CompView.as_view(), name='composicoes'),
    path('comp/teste', TesteView.as_view(), name ='comp_teste'),
]