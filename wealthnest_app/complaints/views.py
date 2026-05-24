from django.shortcuts import render, redirect
from django.contrib import messages
from accounts.decorators import head_required, dependent_required
from accounts.models import Login
from .models import Complaint


def _create(request, template, redirect_to):
    login = Login.objects.get(LOGIN_ID=request.session['login_id'])
    if request.method == 'POST':
        Complaint.objects.create(
            login=login,
            subject=request.POST.get('subject', '').strip(),
            description=request.POST.get('description', '').strip(),
            priority=request.POST.get('priority', 'medium'),
        )
        messages.success(request, 'Complaint submitted.')
        return redirect(redirect_to)
    return render(request, template)


@head_required
def head_complaints(request):
    login = Login.objects.get(LOGIN_ID=request.session['login_id'])
    complaints = Complaint.objects.filter(login=login)
    return render(request, 'head/complaints.html', {'complaints': complaints})


@head_required
def head_complaint_create(request):
    return _create(request, 'head/complaint_create.html', 'head_complaints')


@dependent_required
def dependent_complaints(request):
    login = Login.objects.get(LOGIN_ID=request.session['login_id'])
    complaints = Complaint.objects.filter(login=login)
    return render(request, 'dependent/complaints.html', {'complaints': complaints})


@dependent_required
def dependent_complaint_create(request):
    return _create(request, 'dependent/complaint_create.html', 'dependent_complaints')
