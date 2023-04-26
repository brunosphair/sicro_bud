from django.urls import path

from .views import MeuDetailView

urlpatterns = [
    path('comp/sicro/<str:estado>/<int:ano>/<int:mes>/<str:des>/<str:pk>', MeuDetailView.as_view(), name='composicoes'),
]