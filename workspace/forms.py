from django import forms
from django.contrib.auth import get_user_model
from .models import Client, Project, Task, Invoice


class StyledModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.Select):
                widget.attrs["class"] = "form-select"
            else:
                widget.attrs["class"] = "form-control"


class ClientForm(StyledModelForm):
    class Meta:
        model = Client
        fields = ["name", "company", "email", "phone", "user"]
        labels = {"user": "Client login account (optional)"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["user"].queryset = get_user_model().objects.filter(role="client")
        self.fields["user"].required = False


class ProjectForm(StyledModelForm):
    class Meta:
        model = Project
        fields = ["client", "title", "description", "status", "budget", "deadline"]
        widgets = {"deadline": forms.DateInput(attrs={"type": "date"})}

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields["client"].queryset = Client.objects.filter(freelancer=user)


class TaskForm(StyledModelForm):
    class Meta:
        model = Task
        fields = ["project", "title", "description", "status", "priority", "due_date"]
        widgets = {"due_date": forms.DateInput(attrs={"type": "date"})}

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields["project"].queryset = Project.objects.filter(
                client__freelancer=user
            )

class InvoiceForm(StyledModelForm):
    class Meta:
        model = Invoice
        fields = ["project", "description", "amount", "issue_date", "due_date", "status"]
        widgets = {
            "issue_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "due_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields["project"].queryset = Project.objects.filter(
                client__freelancer=user
            )