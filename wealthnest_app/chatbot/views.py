from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.conf import settings
from accounts.decorators import family_member_required
from accounts.models import Login
from .models import ChatSession, ChatMessage

HEAD_SYSTEM = (
    "You are WealthNest's family finance AI advisor for parents. "
    "Help household heads with: setting effective chore reward amounts, "
    "allowance best practices for different age groups, family budgeting strategies, "
    "teaching financial literacy to children, and platform guidance. "
    "Be practical, warm, and family-focused. Use Indian Rupees (₹) for examples."
)
DEPENDENT_SYSTEM = (
    "You are WealthNest's friendly money coach for young earners! "
    "Help kids and teens with: savings strategies, smart spending habits, "
    "reaching savings goals, understanding the value of money, and platform guidance. "
    "Be fun, encouraging, and age-appropriate. Use simple language and emoji occasionally. "
    "Use Indian Rupees (₹) for examples."
)


def _gemini_reply(history, system_prompt):
    """Call Gemini if API key configured, else return canned reply."""
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        return _canned_reply(history[-1]['content'] if history else '')
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            'gemini-1.5-flash',
            system_instruction=system_prompt,
        )
        chat_history = []
        for msg in history[:-1]:
            chat_history.append({
                'role': 'user' if msg['role'] == 'user' else 'model',
                'parts': [msg['content']],
            })
        chat = model.start_chat(history=chat_history)
        response = chat.send_message(history[-1]['content'])
        return response.text
    except Exception as e:
        return f"I'm having trouble connecting right now. Quick tip: {_canned_reply(history[-1]['content'] if history else '')}\n\n(Error: {str(e)[:80]})"


def _canned_reply(prompt):
    p = prompt.lower()
    if 'reward' in p or 'chore' in p:
        return ("Great question! For chore rewards, a good rule is ₹10–50 for easy tasks (making bed, "
                "tidying), ₹50–100 for medium effort (dishes, laundry), and ₹100–250 for harder, longer "
                "tasks. Match the reward to age and effort, and stay consistent.")
    if 'allowance' in p:
        return ("Allowances work best when they're predictable. A weekly schedule helps young kids learn "
                "patience, while teens often manage better on a monthly cycle. Pair allowance with at "
                "least one savings goal to build the habit early.")
    if 'save' in p or 'saving' in p or 'goal' in p:
        return ("Saving tip: Set a clear goal with a name and a deadline 🎯. Save a small amount every "
                "time you get a reward — even ₹20 adds up! Try the 50/30/20 rule: spend 50%, save 30%, "
                "share 20%.")
    if 'budget' in p:
        return ("Family budgeting is easier when everyone sees the picture. Use WealthNest's analytics to "
                "track which categories grow fastest, and set monthly limits per child's wallet.")
    return ("I'm your WealthNest money coach! Ask me about chores, savings, allowances, budgeting, "
            "or how to use the platform 💰.")


@family_member_required
def chatbot(request):
    login = Login.objects.get(LOGIN_ID=request.session['login_id'])
    sessions = ChatSession.objects.filter(login=login)[:20]
    current_session_id = request.session.get('current_chat_session')
    current_session = None
    msgs = []
    if current_session_id:
        try:
            current_session = ChatSession.objects.get(pk=current_session_id, login=login)
            msgs = list(current_session.messages.all())
        except ChatSession.DoesNotExist:
            pass
    if not current_session:
        current_session = ChatSession.objects.create(login=login, title='New Chat')
        request.session['current_chat_session'] = current_session.session_id

    quick_prompts_head = [
        "How to set effective chore rewards?",
        "Allowance best practices for kids",
        "Family budgeting tips",
        "Teaching kids about saving",
    ]
    quick_prompts_dep = [
        "How do I reach my savings goal faster?",
        "What can I buy with ₹500?",
        "Tips for earning more rewards",
        "Why is saving money important?",
    ]
    return render(request, 'chatbot/chatbot.html', {
        'sessions': sessions,
        'current_session': current_session,
        'msgs': msgs,
        'quick_prompts': quick_prompts_head if login.user_type == 'head' else quick_prompts_dep,
    })


@require_POST
@family_member_required
def send_message(request):
    login = Login.objects.get(LOGIN_ID=request.session['login_id'])
    user_text = request.POST.get('message', '').strip()
    if not user_text:
        return JsonResponse({'error': 'Empty message'}, status=400)

    session_id = request.session.get('current_chat_session')
    session = ChatSession.objects.get(pk=session_id, login=login)

    # Title from first message
    if session.messages.count() == 0:
        session.title = user_text[:50]
        session.save()

    ChatMessage.objects.create(session=session, role='user', content=user_text)

    history = [{'role': m.role, 'content': m.content} for m in session.messages.all()]
    system = HEAD_SYSTEM if login.user_type == 'head' else DEPENDENT_SYSTEM
    reply = _gemini_reply(history, system)
    ChatMessage.objects.create(session=session, role='assistant', content=reply)

    return JsonResponse({'reply': reply})


@family_member_required
def new_chat(request):
    login = Login.objects.get(LOGIN_ID=request.session['login_id'])
    new = ChatSession.objects.create(login=login, title='New Chat')
    request.session['current_chat_session'] = new.session_id
    return redirect('chatbot')


@family_member_required
def load_session(request, pk):
    login = Login.objects.get(LOGIN_ID=request.session['login_id'])
    session = get_object_or_404(ChatSession, pk=pk, login=login)
    request.session['current_chat_session'] = session.session_id
    return redirect('chatbot')
