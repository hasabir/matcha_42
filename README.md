# Matcha 42

A full-stack dating web application built as a 42 school project. It features real-time chat, smart matching, geolocation, and profile browsing.

## Stack

| Layer     | Technology                          |
|-----------|-------------------------------------|
| Backend   | Python 3, Flask, Flask-SocketIO     |
| Frontend  | React                               |
| Database  | PostgreSQL + PostGIS                |
| Cache     | Redis                               |
| Container | Docker & Docker Compose             |

## Getting Started

### 1. Clone the repository

```bash
git clone <repo-url>
cd matcha_42
```

### 2. Configure environment variables

The project **requires a `.env` file** at the root of the repository. Copy the provided template and fill in your values:

```bash
cp .env.example .env
```

Then open `.env` and fill in the required fields:

| Variable                  | Description                                      |
|---------------------------|--------------------------------------------------|
| `DB_NAME`                 | PostgreSQL database name                         |
| `DB_USER`                 | PostgreSQL user                                  |
| `DB_PASSWORD`             | PostgreSQL password                              |
| `JWT_ACCESS_TOKEN`        | Secret key for access tokens                     |
| `JWT_REFRESH_TOKEN`       | Secret key for refresh tokens                    |
| `MAIL_USERNAME`           | SMTP email address (e.g. Gmail)                  |
| `MAIL_PASSWORD`           | SMTP password or app password                    |
| `SMTP_SECRET_KEY`         | Secret key used for email token signing          |
| `PGADMIN_DEFAULT_EMAIL`   | PgAdmin login email                              |
| `PGADMIN_DEFAULT_PASSWORD`| PgAdmin login password                           |

> **SMTP is required.** Email is used for account verification and password reset. Without valid SMTP credentials these features will not work. For Gmail, generate an [App Password](https://myaccount.google.com/apppasswords) and use it as `MAIL_PASSWORD`.

### 3. Start the application

```bash
./cli.py up
```

> Run `./cli.py help` to see all available commands.

### 4. Access the services

| Service  | URL                         |
|----------|-----------------------------|
| Frontend | http://localhost:3000       |
| Backend  | http://localhost:5000       |
| PgAdmin  | http://localhost:5050       |

## CLI Reference

The project ships with a [`cli.py`](cli.py) script that wraps Docker Compose for convenience:

| Command                | Description                                      |
|------------------------|--------------------------------------------------|
| `./cli.py build`       | Build images and start all containers (attached) |
| `./cli.py up`          | Start all containers in detached mode            |
| `./cli.py down`        | Stop and remove all containers                   |
| `./cli.py restart`     | Restart all containers                           |
| `./cli.py ps`          | Show container status                            |
| `./cli.py logs`        | Follow logs for all services                     |
| `./cli.py logs-backend`| Follow backend logs only                         |
| `./cli.py logs-frontend`| Follow frontend logs only                       |
| `./cli.py restart-backend` | Restart only the backend                   |
| `./cli.py restart-frontend`| Restart only the frontend                  |
| `./cli.py rebuild-backend` | Rebuild and restart the backend            |
| `./cli.py rebuild-frontend`| Rebuild and restart the frontend           |
| `./cli.py clean`       | Remove all Docker images and containers          |
| `./cli.py clean-cache` | Prune unused Docker resources                    |
| `./cli.py clean-volumes`| Remove all volumes ⚠️ deletes all data          |
| `./cli.py reset`       | Full reset: stop containers + remove volumes     |
| `./cli.py help`        | Show all available commands                      |

## Features

- User registration, login, and email verification
- Profile setup with photos, interests, and bio
- Smart matching algorithm based on preferences, location, and fame rating
- Real-time chat with Socket.IO
- Like / block / report users
- Geolocation-based browsing
- Notifications (real-time and persistent)


