from django.urls import path
from .views import CompView, CompTodasView, SelectCompsView

urlpatterns = [
    path('comp/sicro/<str:estado>/<int:ano>/<int:mes>/<str:des>/<str:pk>', CompView.as_view(), name='composicoes'),
    path('comp/sicro/<str:estado>/<int:ano>/<int:mes>/<str:des>/', CompTodasView.as_view(), name='comp_todas'),
    path('obra/<int:id>/comps_import/', SelectCompsView.as_view(), name='select_comps'),
]
