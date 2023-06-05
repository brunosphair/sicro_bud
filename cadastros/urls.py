from django.urls import path

from .views import ObraCreate
from .views import ObraUpdate
from .views import ObraDelete
from .views import ObraList
from .views import ObraCompsImportadas
from .views import att_comps_obra


urlpatterns = [
    path('cadastrar/obra/', ObraCreate.as_view(), name='cadastrar-obra'),

    path('editar/obra/<int:pk>/', ObraUpdate.as_view(), name='editar-obra'),

    path('excluir/obra/<int:pk>/', ObraDelete.as_view(), name='excluir-obra'),

    path('listar/obras/', ObraList.as_view(), name='listar-obras'),

    path('api/att-comps-obra/', att_comps_obra, name='api-att-comps-obra'),

    path('obra/<int:id>/comps-importadas/', ObraCompsImportadas.as_view(), name='tab-comps-importadas'),
]
