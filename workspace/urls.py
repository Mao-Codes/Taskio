from django.urls import path
from . import views

app_name = "workspace"
urlpatterns = [
    path("", views.dashboard, name="dashboard"),

    path("clients/", views.ClientList.as_view(), name="client_list"),
    path("clients/add/", views.ClientCreate.as_view(), name="client_add"),
    path("clients/<int:pk>/edit/", views.ClientUpdate.as_view(), name="client_edit"),
    path("clients/<int:pk>/delete/", views.ClientDelete.as_view(), name="client_delete"),

    path("projects/", views.ProjectList.as_view(), name="project_list"),
    path("projects/add/", views.ProjectCreate.as_view(), name="project_add"),
    path("projects/<int:pk>/edit/", views.ProjectUpdate.as_view(), name="project_edit"),
    path("projects/<int:pk>/delete/", views.ProjectDelete.as_view(), name="project_delete"),

    path("tasks/", views.TaskList.as_view(), name="task_list"),
    path("tasks/add/", views.TaskCreate.as_view(), name="task_add"),
    path("tasks/<int:pk>/edit/", views.TaskUpdate.as_view(), name="task_edit"),
    path("tasks/<int:pk>/delete/", views.TaskDelete.as_view(), name="task_delete"),
    path("tasks/<int:pk>/complete/", views.task_complete, name="task_complete"),
    path("tasks/<int:pk>/thread/", views.task_thread, name="task_thread"),

    path("invoices/", views.InvoiceList.as_view(), name="invoice_list"),
    path("invoices/add/", views.InvoiceCreate.as_view(), name="invoice_add"),
    path("invoices/<int:pk>/edit/", views.InvoiceUpdate.as_view(), name="invoice_edit"),
    path("invoices/<int:pk>/delete/", views.InvoiceDelete.as_view(), name="invoice_delete"),
    path("invoices/<int:pk>/toggle/", views.invoice_toggle, name="invoice_toggle"),
]