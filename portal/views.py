from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404

from workspace.models import Client, Project, Task, Invoice

@login_required
def dashboard(request):
    if request.user.is_freelancer:
        return redirect("workspace:dashboard")

    client = Client.objects.filter(user=request.user).first()
    projects = Project.objects.filter(client=client) if client else Project.objects.none()
    tasks = Task.objects.filter(project__in=projects)

    context = {
        "client": client,
        "projects": projects,
        "project_count": projects.count(),
        "awaiting": tasks.filter(status="review").count(),
        "completed": tasks.filter(status="done").count(),
    }
    return render(request, "portal/dashboard.html", context)


@login_required
def project_detail(request, pk):
    if request.user.is_freelancer:
        return redirect("workspace:dashboard")
    project = get_object_or_404(Project, pk=pk, client__user=request.user)
    return render(
        request,
        "portal/project_detail.html",
        {"project": project, "tasks": project.tasks.all()},
    )


@login_required
def task_review(request, pk, action):
    task = get_object_or_404(Task, pk=pk, project__client__user=request.user)
    if request.method == "POST" and task.status == "review":
        if action == "approve":
            task.status = "done"
        elif action == "changes":
            task.status = "in_progress"
        task.save()
    return redirect("portal:project_detail", pk=task.project.pk)

@login_required
def invoices(request):
    if request.user.is_freelancer:
        return redirect("workspace:invoice_list")
    items = Invoice.objects.filter(
        project__client__user=request.user
    ).select_related("project")
    outstanding = items.filter(status="unpaid").aggregate(t=Sum("amount"))["t"] or 0
    return render(
        request, "portal/invoices.html", {"invoices": items, "outstanding": outstanding}
    )