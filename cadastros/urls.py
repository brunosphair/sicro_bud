from django.urls import path

from .views import ObraCreate
from .views import ObraUpdate
from .views import ObraDelete
from .views import ObraList
from .views import ObraTeste
from .views import adicionar_linha, autocompletar_lista


urlpatterns = [
    path('cadastrar/obra/', ObraCreate.as_view(), name='cadastrar-obra'),

    path('editar/obra/<int:pk>/', ObraUpdate.as_view(), name='editar-obra'),

    path('excluir/obra/<int:pk>/', ObraDelete.as_view(), name='excluir-obra'),

    path('listar/obras/', ObraList.as_view(), name='listar-obras'),

    path('teste/obra/', ObraTeste.as_view(), name='teste-obra'),

    path('teste/obra/adicionar_linha/', adicionar_linha, name='adicionar_linha'),

    path('teste/obra/autocompletar_lista/', autocompletar_lista, name='autocompletar_lista'),
    
]