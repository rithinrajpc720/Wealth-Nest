from django.db import models


class ChoreCategory(models.Model):
    name = models.CharField(max_length=50, unique=True)
    icon = models.CharField(max_length=10, default='🧹')
    color = models.CharField(max_length=7, default='#1E1B4B')

    class Meta:
        db_table = 'chore_category'
        verbose_name_plural = 'Chore Categories'

    def __str__(self):
        return self.name


class Chore(models.Model):
    DIFFICULTIES = [('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard')]
    STATUSES = [
        ('active', 'Active'),
        ('pending_approval', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('archived', 'Archived'),
    ]
    RECURRING = [('weekly', 'Weekly'), ('monthly', 'Monthly')]

    chore_id = models.AutoField(primary_key=True)
    family = models.ForeignKey('families.Family', on_delete=models.CASCADE)
    assigned_by = models.ForeignKey('heads.HouseholdHead', on_delete=models.CASCADE)
    assigned_to = models.ForeignKey('dependents.FamilyDependent', on_delete=models.CASCADE)
    category = models.ForeignKey(ChoreCategory, on_delete=models.SET_NULL, null=True, blank=True)
    chore_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    reward_amount = models.FloatField()
    difficulty = models.CharField(max_length=10, choices=DIFFICULTIES, default='easy')
    deadline = models.DateField()
    is_recurring = models.BooleanField(default=False)
    recurring_type = models.CharField(max_length=10, choices=RECURRING, blank=True)
    status = models.CharField(max_length=20, choices=STATUSES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'chore'
        ordering = ['-created_at']

    def __str__(self):
        return self.chore_name

    @property
    def difficulty_color(self):
        return {'easy': '#10B981', 'medium': '#F6C90E', 'hard': '#FF6B6B'}.get(self.difficulty, '#6B7280')

    @property
    def status_color(self):
        return {
            'active': '#10B981',
            'pending_approval': '#F6C90E',
            'approved': '#8B5CF6',
            'rejected': '#FF6B6B',
            'archived': '#6B7280',
        }.get(self.status, '#6B7280')


class ChoreSubmission(models.Model):
    submission_id = models.AutoField(primary_key=True)
    chore = models.ForeignKey(Chore, on_delete=models.CASCADE)
    dependent = models.ForeignKey('dependents.FamilyDependent', on_delete=models.CASCADE)
    completion_notes = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    is_approved = models.BooleanField(null=True)
    rejection_reason = models.TextField(blank=True)

    class Meta:
        db_table = 'chore_submission'
        ordering = ['-submitted_at']

    def __str__(self):
        return f"Submission #{self.submission_id} - {self.chore.chore_name}"
