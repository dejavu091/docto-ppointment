# docto-ppointment

A Django-based appointment booking and contact management application with product listing, pricing plans, email notifications, and optional Cloudinary media storage.

## Website

- https://docto-ppointment.onrender.com/ (production)

## Features

- Appointment booking form on the homepage
- Contact inquiry form with admin notification emails
- Product listing with superuser-only product upload
- Pricing plans seeded automatically if none exist
- Django admin available at `/dejavu/`
- Cloudinary media storage for uploaded files
- Default SQLite database fallback when no external database URL is configured

## Tech stack

- Python 3.14
- Django 6.0.7
- Cloudinary + `django-cloudinary-storage`
- Whitenoise for static file handling
- `dj-database-url` for database URL parsing

## Installation

1. Clone the repo:

```powershell
cd "C:\Users\ADEDEJI ADEYEMI\Desktop\docto-ppointment"
```

2. Create and activate the virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Install dependencies:

```powershell
pip install -r requirements.txt
```

4. Create a `.env` file in the project root and add required settings.

## Environment variables

Required variables:

- `SECRET_KEY`
- `DEBUG` (set to `True` or `False`)
- `DATABASE_URL` (optional; if not provided, SQLite is used automatically)
- `CLOUDINARY_CLOUD_NAME`
- `CLOUDINARY_API_KEY`
- `CLOUDINARY_API_SECRET`

Optional variables:

- `DJANGO_EMAIL_BACKEND`
- `EMAIL_HOST`
- `EMAIL_PORT`
- `EMAIL_HOST_USER`
- `EMAIL_HOST_PASSWORD`
- `EMAIL_USE_TLS`
- `EMAIL_USE_SSL`
- `DEFAULT_FROM_EMAIL`

Example `.env`:

```env
SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
DEFAULT_FROM_EMAIL=no-reply@docto-ppointment.local
```

## Database

The project uses SQLite by default. If you set `DATABASE_URL`, the app will use that database instead. Common examples:

```env
DATABASE_URL=postgres://user:password@host:port/dbname
```

## Run locally

```powershell
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Then open `http://127.0.0.1:8000/`.

## Admin

- Admin URL: `/dejavu/`
- Use the superuser account created with `createsuperuser`

## App routes

- `/` - Home / appointment booking
- `/products/` - Product catalog and upload for superusers
- `/pricing/` - Pricing plans
- `/contact/` - Contact inquiry form
- `/about/` - About page

## Notes

- Uploaded media is stored through Cloudinary via `cloudinary_storage`.
- `staticfiles/` is the collectstatic output directory.
- The app uses `django.contrib.staticfiles` and Whitenoise for static handling.
