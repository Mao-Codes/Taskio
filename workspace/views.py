from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from .forms import ClientForm, ProjectForm, TaskForm, InvoiceForm

from django.db.models import Q, Sum
from .models import Client, Project, Task, Invoice, Comment



@login_required
def dashboard(request):
    if request.user.is_client:
        return redirect("portal:dashboard")

    today = timezone.localdate()
    week_end = today + timedelta(days=7)

    tasks = Task.objects.filter(project__client__freelancer=request.user)
    open_tasks = tasks.exclude(status="done")
    invoices = Invoice.objects.filter(project__client__freelancer=request.user)

    status_counts = [
        tasks.filter(status=key).count() for key, _ in Task.Status.choices
    ]
    status_labels = [label for _, label in Task.Status.choices]

    paid_total = invoices.filter(status="paid").aggregate(t=Sum("amount"))["t"] or 0
    unpaid_total = invoices.filter(status="unpaid").aggregate(t=Sum("amount"))["t"] or 0

    context = {
        "client_count": Client.objects.filter(freelancer=request.user).count(),
        "active_projects": Project.objects.filter(
            client__freelancer=request.user, status="active"
        ).count(),
        "due_this_week": open_tasks.filter(due_date__range=(today, week_end)).count(),
        "overdue": open_tasks.filter(due_date__lt=today).count(),
        "upcoming_tasks": open_tasks.select_related("project__client")[:6],
        "projects": Project.objects.filter(
            client__freelancer=request.user, status="active"
        ).select_related("client")[:5],
        "status_labels": status_labels,
        "status_counts": status_counts,
        "paid_total": float(paid_total),
        "unpaid_total": float(unpaid_total),
    }
    return render(request, "workspace/dashboard.html", context)

class FreelancerOnly(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_freelancer


class UserFormMixin:
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


# ---------- Clients ----------
class ClientList(FreelancerOnly, ListView):
    template_name = "workspace/client_list.html"
    context_object_name = "clients"

    def get_queryset(self):
        return Client.objects.filter(freelancer=self.request.user)


class ClientCreate(FreelancerOnly, CreateView):
    form_class = ClientForm
    template_name = "workspace/form.html"
    success_url = reverse_lazy("workspace:client_list")
    extra_context = {"heading": "Add Client"}

    def form_valid(self, form):
        form.instance.freelancer = self.request.user
        return super().form_valid(form)


class ClientUpdate(FreelancerOnly, UpdateView):
    form_class = ClientForm
    template_name = "workspace/form.html"
    success_url = reverse_lazy("workspace:client_list")
    extra_context = {"heading": "Edit Client"}

    def get_queryset(self):
        return Client.objects.filter(freelancer=self.request.user)


class ClientDelete(FreelancerOnly, DeleteView):
    template_name = "workspace/confirm_delete.html"
    success_url = reverse_lazy("workspace:client_list")

    def get_queryset(self):
        return Client.objects.filter(freelancer=self.request.user)


# ---------- Projects ----------
class ProjectList(FreelancerOnly, ListView):
    template_name = "workspace/project_list.html"
    context_object_name = "projects"

    def get_queryset(self):
        return Project.objects.filter(
            client__freelancer=self.request.user
        ).select_related("client")


class ProjectCreate(FreelancerOnly, UserFormMixin, CreateView):
    form_class = ProjectForm
    template_name = "workspace/form.html"
    success_url = reverse_lazy("workspace:project_list")
    extra_context = {"heading": "Add Project"}


class ProjectUpdate(FreelancerOnly, UserFormMixin, UpdateView):
    form_class = ProjectForm
    template_name = "workspace/form.html"
    success_url = reverse_lazy("workspace:project_list")
    extra_context = {"heading": "Edit Project"}

    def get_queryset(self):
        return Project.objects.filter(client__freelancer=self.request.user)


class ProjectDelete(FreelancerOnly, DeleteView):
    template_name = "workspace/confirm_delete.html"
    success_url = reverse_lazy("workspace:project_list")

    def get_queryset(self):
        return Project.objects.filter(client__freelancer=self.request.user)


# ---------- Tasks ----------
class TaskList(FreelancerOnly, ListView):
    template_name = "workspace/task_list.html"
    context_object_name = "tasks"

    def get_queryset(self):
        return Task.objects.filter(
            project__client__freelancer=self.request.user
        ).select_related("project__client")


class TaskCreate(FreelancerOnly, UserFormMixin, CreateView):
    form_class = TaskForm
    template_name = "workspace/form.html"
    success_url = reverse_lazy("workspace:task_list")
    extra_context = {"heading": "Add Task"}


class TaskUpdate(FreelancerOnly, UserFormMixin, UpdateView):
    form_class = TaskForm
    template_name = "workspace/form.html"
    success_url = reverse_lazy("workspace:task_list")
    extra_context = {"heading": "Edit Task"}

    def get_queryset(self):
        return Task.objects.filter(project__client__freelancer=self.request.user)


class TaskDelete(FreelancerOnly, DeleteView):
    template_name = "workspace/confirm_delete.html"
    success_url = reverse_lazy("workspace:task_list")

    def get_queryset(self):
        return Task.objects.filter(project__client__freelancer=self.request.user)


@login_required
def task_complete(request, pk):
    task = Task.objects.get(pk=pk, project__client__freelancer=request.user)
    if request.method == "POST":
        task.status = "done"
        task.save()
    return redirect("workspace:task_list")

# ---------- Invoices ----------
class InvoiceList(FreelancerOnly, ListView):
    template_name = "workspace/invoice_list.html"
    context_object_name = "invoices"

    def get_queryset(self):
        return Invoice.objects.filter(
            project__client__freelancer=self.request.user
        ).select_related("project__client")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        qs = self.get_queryset()
        ctx["outstanding"] = qs.filter(status="unpaid").aggregate(t=Sum("amount"))["t"] or 0
        ctx["earned"] = qs.filter(status="paid").aggregate(t=Sum("amount"))["t"] or 0
        return ctx


class InvoiceCreate(FreelancerOnly, UserFormMixin, CreateView):
    form_class = InvoiceForm
    template_name = "workspace/form.html"
    success_url = reverse_lazy("workspace:invoice_list")
    extra_context = {"heading": "Create Invoice"}


class InvoiceUpdate(FreelancerOnly, UserFormMixin, UpdateView):
    form_class = InvoiceForm
    template_name = "workspace/form.html"
    success_url = reverse_lazy("workspace:invoice_list")
    extra_context = {"heading": "Edit Invoice"}

    def get_queryset(self):
        return Invoice.objects.filter(project__client__freelancer=self.request.user)


class InvoiceDelete(FreelancerOnly, DeleteView):
    template_name = "workspace/confirm_delete.html"
    success_url = reverse_lazy("workspace:invoice_list")

    def get_queryset(self):
        return Invoice.objects.filter(project__client__freelancer=self.request.user)


@login_required
def invoice_toggle(request, pk):
    inv = get_object_or_404(Invoice, pk=pk, project__client__freelancer=request.user)
    if request.method == "POST":
        if inv.status == "paid":
            inv.status = "unpaid"
            inv.paid_on = None
        else:
            inv.status = "paid"
            inv.paid_on = timezone.localdate()
        inv.save()
    return redirect("workspace:invoice_list")

@login_required
def task_thread(request, pk):
    user = request.user
    task = get_object_or_404(
        Task.objects.select_related("project__client"),
        Q(project__client__freelancer=user) | Q(project__client__user=user),
        pk=pk,
    )

    if request.method == "POST":
        body = request.POST.get("body", "").strip()
        if body:
            Comment.objects.create(task=task, author=user, body=body)
        return redirect("workspace:task_thread", pk=task.pk)

    back_url = "workspace:task_list" if user.is_freelancer else "portal:project_detail"
    back_args = [] if user.is_freelancer else [task.project.pk]

    return render(
        request,
        "workspace/task_thread.html",
        {
            "task": task,
            "comments": task.comments.select_related("author"),
            "back_url": back_url,
            "back_args": back_args,
        },
    )

@login_required
def task_thread(request, pk):
    user = request.user
    task = get_object_or_404(
        Task.objects.select_related("project__client"),
        Q(project__client__freelancer=user) | Q(project__client__user=user),
        pk=pk,
    )

    if request.method == "POST":
        body = request.POST.get("body", "").strip()
        if body:
            Comment.objects.create(task=task, author=user, body=body)
        return redirect("workspace:task_thread", pk=task.pk)

    return render(
        request,
        "workspace/task_thread.html",
        {"task": task, "comments": task.comments.select_related("author")},
    )