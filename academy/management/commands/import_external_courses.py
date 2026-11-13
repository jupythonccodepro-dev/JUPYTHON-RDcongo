import csv
import json
from pathlib import Path
from urllib.parse import urlsplit

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.core.validators import URLValidator
from django.db import transaction

from academy.models import Formation


FIELDS = (
    'title',
    'platform',
    'link',
    'is_free',
    'description',
    'domain',
    'level',
    'duration',
    'language',
    'skills',
    'credential_info',
    'cover_image_url',
    'provider_logo_url',
)
REQUIRED = ('title', 'platform', 'link')
MAX_LENGTHS = {
    'title': 200,
    'platform': 100,
    'domain': 100,
    'level': 50,
    'duration': 100,
    'language': 100,
}
URL_FIELDS = ('link', 'cover_image_url', 'provider_logo_url')
FREE_VALUES = {'1': True, 'true': True, 'yes': True, 'y': True, '0': False, 'false': False, 'no': False, 'n': False}


class Command(BaseCommand):
    help = 'Preview or import external formations from a curated CSV file.'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=Path)
        parser.add_argument(
            '--apply',
            action='store_true',
            help='Save validated rows. Without this flag the command only previews changes.',
        )

    def handle(self, *args, **options):
        csv_path = options['csv_file']
        try:
            with csv_path.open('r', encoding='utf-8-sig', newline='') as source:
                reader = csv.DictReader(source)
                headers = set(reader.fieldnames or [])
                missing = set(REQUIRED) - headers
                if missing:
                    raise CommandError(f'Missing required CSV columns: {", ".join(sorted(missing))}')
                rows = list(reader)
        except OSError as exc:
            raise CommandError(f'Cannot read CSV file: {csv_path}') from exc
        if not rows:
            raise CommandError('The CSV contains no course rows.')

        validator = URLValidator(schemes=['https'])
        seen_links = set()
        plan = []
        errors = []
        for row_number, raw_row in enumerate(rows, start=2):
            values = {field: (raw_row.get(field) or '').strip() for field in FIELDS if field in headers}
            row_errors = []
            for field in REQUIRED:
                if not values.get(field):
                    row_errors.append(f'{field} is required')
            for field, max_length in MAX_LENGTHS.items():
                if len(values.get(field, '')) > max_length:
                    row_errors.append(f'{field} exceeds {max_length} characters')
            for field in URL_FIELDS:
                if field not in values:
                    continue
                url = values[field]
                if not url:
                    if field in REQUIRED:
                        continue
                    values[field] = ''
                    continue
                try:
                    validator(url)
                    if urlsplit(url).scheme != 'https':
                        row_errors.append(f'{field} must use HTTPS')
                except ValidationError:
                    row_errors.append(f'{field} must be a valid HTTPS URL')

            if values.get('link'):
                if values['link'] in seen_links:
                    row_errors.append('link is duplicated in this CSV')
                seen_links.add(values['link'])
            if 'is_free' in values:
                free_value = values['is_free'].lower() or 'true'
                if free_value not in FREE_VALUES:
                    row_errors.append('is_free must be true/false, yes/no, or 1/0')
                else:
                    values['is_free'] = FREE_VALUES[free_value]

            skills_value = values.get('skills', '')
            if 'skills' in values and skills_value:
                try:
                    skills = json.loads(skills_value) if skills_value.startswith('[') else skills_value.split(';')
                    if not isinstance(skills, list) or not all(isinstance(item, str) for item in skills):
                        raise ValueError
                    values['skills'] = [item.strip() for item in skills if item.strip()]
                except (json.JSONDecodeError, ValueError):
                    row_errors.append('skills must be a JSON string array or semicolon-separated text')
            elif 'skills' in values:
                values['skills'] = []

            if row_errors:
                errors.append(f'Row {row_number}: {"; ".join(row_errors)}')
                continue

            matches = Formation.objects.filter(link=values['link'], hosted_by_jupython=False).order_by('id')
            if matches.count() > 1:
                errors.append(f'Row {row_number}: multiple external formations already use this link')
                continue
            existing = matches.first()
            plan.append((row_number, existing, values))

        if errors:
            for error in errors:
                self.stderr.write(self.style.ERROR(error))
            raise CommandError(f'Import cancelled; {len(errors)} row(s) need correction. No changes were saved.')

        creates = sum(existing is None for _, existing, _ in plan)
        updates = len(plan) - creates
        self.stdout.write(f'Validated {len(plan)} external course row(s): {creates} new, {updates} update(s).')
        if not options['apply']:
            self.stdout.write('Preview only; pass --apply to save these changes.')
            return

        with transaction.atomic():
            for _, existing, values in plan:
                if existing is None:
                    Formation.objects.create(hosted_by_jupython=False, **values)
                else:
                    for field, value in values.items():
                        setattr(existing, field, value)
                    existing.save(update_fields=list(values.keys()))
        self.stdout.write(self.style.SUCCESS('Course import completed. Review the imported entries in Django admin before sharing them.'))
