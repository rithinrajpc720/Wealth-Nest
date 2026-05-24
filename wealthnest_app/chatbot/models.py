from django.db import models


class ChatSession(models.Model):
    session_id = models.AutoField(primary_key=True)
    login = models.ForeignKey('accounts.Login', on_delete=models.CASCADE)
    title = models.CharField(max_length=200, default='New Chat')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'chat_session'
        ordering = ['-updated_at']


class ChatMessage(models.Model):
    ROLES = [('user', 'User'), ('assistant', 'Assistant')]
    message_id = models.AutoField(primary_key=True)
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=15, choices=ROLES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'chat_message'
        ordering = ['created_at']
