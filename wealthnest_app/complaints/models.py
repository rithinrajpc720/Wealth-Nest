from django.db import models


class Complaint(models.Model):
    STATUSES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    PRIORITIES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    complaint_id = models.AutoField(primary_key=True)
    login = models.ForeignKey('accounts.Login', on_delete=models.CASCADE)
    subject = models.CharField(max_length=200)
    description = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITIES, default='medium')
    status = models.CharField(max_length=15, choices=STATUSES, default='open')
    admin_response = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'complaint'
        ordering = ['-created_at']

    def __str__(self):
        return self.subject
