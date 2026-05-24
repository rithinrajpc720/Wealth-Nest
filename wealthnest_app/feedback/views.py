from django.shortcuts import render, redirect
from django.contrib import messages
from accounts.decorators import head_required, dependent_required
from accounts.models import Login
from .models import Feedback


def _submit(request, template, redirect_to):
    login = Login.objects.get(LOGIN_ID=request.session['login_id'])
    if request.method == 'POST':
        Feedback.objects.create(
            login=login,
            rating=int(request.POST.get('rating', 5)),
            subject=request.POST.get('subject', '').strip(),
            message=request.POST.get('message', '').strip(),
        )
        messages.success(request, 'Thanks for your feedback! 💙')
        return redirect(redirect_to)
    feedback_list = Feedback.objects.filter(login=login)
    return render(request, template, {'feedback_list': feedback_list})


@head_required
def head_feedback(request):
    return _submit(request, 'head/feedback.html', 'head_feedback')


@dependent_required
def dependent_feedback(request):
    return _submit(request, 'dependent/feedback.html', 'dependent_feedback')
