# PaperMetrix

PaperMetrix is a Django based platform for managing and recommending academic articles.

## Setup

1. Install Python 3 and [Redis](https://redis.io) along with MySQL.
2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and update the values as needed.
4. Run database migrations:
   ```bash
   python manage.py migrate
   ```
5. Start the development server:
   ```bash
   python manage.py runserver
   ```
6. To install dependencies in a virtual environment run:
   ```bash
   ./scripts/setup.sh
   ```

## Recommendation Tasks

Run Celery workers to process background jobs:
```bash
redis-server
./worker.sh
./beat.sh
```

## Environment Variables

The project reads configuration from environment variables. The `.env.example` file
lists the variables used:

- `SECRET_KEY` – Django secret key
- `MYSQL_DATABASE` – database name
- `MYSQL_USER` – database user
- `MYSQL_PASSWORD` – database password
- `MYSQL_HOST` – database host (default `localhost`)
- `MYSQL_PORT` – database port (default `3306`)
- `MENDELEY_SECRET` – API secret for Mendeley integration
- `MENDELEY_ID` – Mendeley client ID
- `DEEPSEEK_API_KEY` – API key for DeepSeek
- `EMAIL_HOST_USER` – email account used for sending mail
- `EMAIL_HOST_PASSWORD` – password for the email account

Create a `.env` file with these values before running the application.

## Celery Workers

Background tasks rely on Celery and Redis. Two helper scripts are provided:

- `worker.sh` – runs the Celery worker
- `beat.sh` – runs the Celery beat scheduler

Make the scripts executable and run them in separate terminals alongside a
Redis server:

```bash
chmod +x worker.sh beat.sh
redis-server
./worker.sh
./beat.sh
```

Celery beat schedules tasks such as sending recommendation emails while the
worker executes them.
