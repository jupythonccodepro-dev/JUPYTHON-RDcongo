from django.shortcuts import render


def contact_view(request):
    return render(request, 'contact.html', {})


def about_view(request):
    return render(request, 'about.html', {})


def health_check(request):
    from django.db import connection
    from django.http import JsonResponse

    try:
        connection.ensure_connection()
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
            cursor.fetchone()
    except Exception:
        return JsonResponse({'status': 'unavailable'}, status=503)
    return JsonResponse({'status': 'ok'})
