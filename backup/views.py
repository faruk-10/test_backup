# Create your views here.
from django.http import JsonResponse
from django.core.management import call_command

def trigger_backup(request):
    call_command('backup_db')
    return JsonResponse({'status': 'Backup triggered'})

def restore_backup(request):
    try:
        call_command('restore_db')
        return JsonResponse({'status': 'Backup triggered'})
    except Exception as e:
        return JsonResponse({'status': f'Backup triggered{e}'})