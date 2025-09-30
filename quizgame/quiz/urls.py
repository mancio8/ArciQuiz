from django.urls import path
from . import views

urlpatterns = [
    path("current/", views.current_question, name="current_question"),
    path("conductor/", views.conductor_dashboard, name="conductor_dashboard"),
    path("set/<int:qid>/", views.set_question, name="set_question"),
    path("buzz/", views.buzz, name="buzz"),
    path("add/<int:team>/", views.add_point, name="add_point"),
    path("wrong/", views.wrong_answer, name="wrong_answer"),
    path('reset/', views.reset_game, name='reset_game'),

]
