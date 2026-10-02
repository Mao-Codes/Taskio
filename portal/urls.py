from django.urls import path
from . import views

app_name = "portal"
urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("projects/<int:pk>/", views.project_detail, name="project_detail"),
    path("tasks/<int:pk>/<str:action>/", views.task_review, name="task_review"),
    path("invoices/", views.invoices, name="invoices"),
]