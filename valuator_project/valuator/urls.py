from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.render_main),
    path('ajax/proces_road/', views.proces_road, name='proces_road'),
    path('ajax/resolve_location/', views.resolve_location, name='proces_road'),
    ]
