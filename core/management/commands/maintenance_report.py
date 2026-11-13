from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.core.mail import send_mail
from django.db import connection
from django.db.models import Q
from django.utils import timezone

from academy.models import Certificate, Formation
from core.models import ContactMessage


class Command(BaseCommand):
    help = 'Summarize site maintenance items without changing site data.'

    def handle(self, *args, **options):
        try:
            connection.ensure_connection()
            with connection.cursor() as cursor:
                cursor.execute('SELECT 1')
                cursor.fetchone()
        except Exception as exc:
            raise CommandError('Database health check failed.') from exc

        stale_before = timezone.now() - timedelta(days=30)
        stale_count = Formation.objects.filter(
            hosted_by_jupython=False,
        ).filter(
            Q(last_verified_at__isnull=True) | Q(last_verified_at__lt=stale_before),
        ).count()
        unreviewed_certificates = Certificate.objects.filter(verified=False).count()
        recent_contact_messages = ContactMessage.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=7),
        ).count()

        report = [
            'Jupython site maintenance report',
            f'Generated at (UTC): {timezone.now().isoformat()}',
            'Database: OK',
            f'External courses needing review (>30 days or never reviewed): {stale_count}',
            f'External certificate submissions awaiting review: {unreviewed_certificates}',
            f'Contact messages received in the last 7 days: {recent_contact_messages}',
        ]
        report_text = '\n'.join(report)
        self.stdout.write(report_text)

        recipient = settings.MAINTENANCE_REPORT_EMAIL
        if recipient:
            send_mail(
                subject='Jupython daily maintenance report',
                message=report_text,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient],
                fail_silently=False,
            )
            self.stdout.write(f'Report sent to {recipient}.')
