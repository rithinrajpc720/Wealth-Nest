from django.db import models


class Feedback(models.Model):
    feedback_id = models.AutoField(primary_key=True)
    login = models.ForeignKey('accounts.Login', on_delete=models.CASCADE)
    rating = models.IntegerField(default=5)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'feedback'
        ordering = ['-created_at']

    def __str__(self):
        return self.subject
