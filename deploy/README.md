# Oracle Cloud deployment preparation

This deployment pack runs the Django site, PostgreSQL, Caddy HTTPS, static files,
media uploads, a daily maintenance report, and daily database/media backups on one VM.
The Compose stack is separate from the existing local-development Compose file.

## Before creating the VM

1. Create an Oracle Cloud Free Tier account. Choose a home region with free VM
   capacity. Oracle typically verifies new accounts with a phone number and card.
2. Create an Ubuntu ARM64 VM eligible for the Always Free allowance.
3. Assign a reserved public IP. Point an A record for your domain to that IP.
4. In the OCI network security list, allow inbound TCP 80 and 443. Allow SSH
   (TCP 22) from your own IP only. Do not expose PostgreSQL port 5432.
5. Install Docker Engine, the Docker Compose plugin, cron, logrotate, and OCI CLI
   using their official Ubuntu/Oracle instructions.

## Deploy the site

From the VM, clone this repository to `/opt/jupython`, then:

```bash
cd /opt/jupython
# Use the branch that contains the reviewed deployment files.
cp deploy/production.example.env deploy/production.env
chmod 600 deploy/production.env
nano deploy/production.env
```

Set `DOMAIN`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `CORS_ALLOWED_ORIGINS`,
`SECRET_KEY`, and `POSTGRES_PASSWORD`. Ensure DNS already points
at this VM before starting Caddy; Caddy obtains and renews the HTTPS certificate.
Set up Google OAuth and SMTP only if those features are needed. Keep
`deploy/production.env` private and never commit it.

Build and start the services:

```bash
docker compose --env-file deploy/production.env -f deploy/docker-compose.yml up -d --build
```

The app applies migrations and collects static files before starting Gunicorn.
PostgreSQL data and uploaded profile/course images use persistent Docker volumes.
Create the first administrator:

```bash
docker compose --env-file deploy/production.env -f deploy/docker-compose.yml run --rm app python manage.py createsuperuser
```

## Import curated external courses

Prepare a CSV from `external-courses.template.csv`. The required columns are
`title`, `platform`, and an HTTPS `link`. Optional `skills` is a JSON array or
semicolon-separated list. Imported courses are never marked as verified by the
importer. The first command only validates and previews; `--apply` saves the
rows and updates existing external courses by exact HTTPS link.

On the VM, place the reviewed CSV at `/opt/jupython/deploy/external-courses.csv`
then run:

```bash
docker compose --env-file deploy/production.env -f deploy/docker-compose.yml run --rm \
  -v /opt/jupython/deploy/external-courses.csv:/tmp/external-courses.csv:ro app \
  python manage.py import_external_courses /tmp/external-courses.csv
```

Review the preview. If it is correct, repeat with `--apply`, then inspect the
entries in Django admin. This import is an explicit reviewed action; it does not
scrape partner sites or publish unverified partner data automatically.

## Daily maintenance and backups

Install the host's daily cron entries:

```bash
sudo bash ./deploy/install-scheduled-tasks.sh
```

The report runs daily at 03:15 server local time and counts external courses that need review,
certificate submissions awaiting review, recent contact messages, and database
health. If `MAINTENANCE_REPORT_EMAIL` and SMTP are configured, it emails the
summary. Leave `MAINTENANCE_REPORT_EMAIL` blank until SMTP credentials work. Otherwise it appears in `/var/log/jupython/maintenance.log`.

Compressed PostgreSQL and media backups run daily at 03:45 server local time
under `/var/backups/jupython`. Local backup files older than 30 days are removed.
By default these backups stay on the VM, so they cannot protect against loss of
the VM.

For off-instance copies, create an OCI Object Storage bucket, install OCI CLI,
and set up a dynamic group and policy that grants this VM access only to that
bucket. Copy `deploy/backup.env.example` to `deploy/backup.env` and set the bucket
name and the VM's OCI region. The script uploads both backup files with instance
principal authentication; it stores no API key. Apply an Object Storage lifecycle
rule to control retention and keep usage within the Always Free quota. Without
this setup, there is no off-site backup.

Restore only after verifying both archives. Load the SQL dump into a separate
clean PostgreSQL database and extract the media archive to a separate directory;
do not restore over production without a separately reviewed recovery plan.
## Updates

After publishing a reviewed code update to the repository:

```bash
cd /opt/jupython
git pull --ff-only
docker compose --env-file deploy/production.env -f deploy/docker-compose.yml up -d --build
```

The platform does not automatically add courses from partner sites. Keep the
existing admin review step: many providers have no public catalogue feed, and
price, language, links, and certification details need verification before
publication. This deployment's daily report identifies courses due for review.
