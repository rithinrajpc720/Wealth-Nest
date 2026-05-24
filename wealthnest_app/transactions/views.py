import csv
from django.http import HttpResponse
from accounts.decorators import head_required
from heads.models import HouseholdHead
from .models import Transaction


@head_required
def export_family_csv(request):
    head = HouseholdHead.objects.get(head_id=request.session['head_id'])
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="family_transactions_{head.family.family_name}.csv"'
    writer = csv.writer(response)
    writer.writerow(['Member', 'Type', 'Category', 'Amount', 'Description', 'Date'])
    for t in Transaction.objects.filter(dependent__family=head.family).order_by('-created_at'):
        writer.writerow([
            t.dependent.full_name, t.transaction_type, t.category,
            t.amount, t.description, t.created_at.strftime('%Y-%m-%d %H:%M'),
        ])
    return response
