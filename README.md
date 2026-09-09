# Messenger

A real-time messenger application built with Python.

The project uses **Django** as the main backend and **FastAPI** as a separate real-time service for WebSocket communication.

## Architecture

```text
                         ┌──────────────┐
                         │   Frontend   │
                         └──────┬───────┘
                                │
                   ┌────────────┴────────────┐
                   │                         │
                HTTP/REST                WebSocket
                   │                         │
                   ▼                         ▼
           ┌───────────────┐        ┌─────────────────┐
           │ Django + DRF  │        │     FastAPI     │
           │    Backend    │        │ Realtime Service│
           └───────┬───────┘        └────────┬────────┘
                   │                         │
                   └──────────┬──────────────┘
                              │
                              ▼
                     ┌─────────────────┐
                     │   PostgreSQL    │
                     └─────────────────┘
                              │
                              ▼
                     ┌─────────────────┐
                     │      Redis      │
                     └─────────────────┘
```

### Backend

Django and Django REST Framework are responsible for:

* Authentication and authorization
* Users
* Conversations
* Messages
* Business logic
* REST API
* Database operations

### Realtime Service

FastAPI handles real-time communication through WebSockets.

Redis is used for communication between real-time service instances and other backend components.

### Frontend

The frontend provides the client interface for interacting with the messenger.

## Project Structure

```text
messenger/
│
├── backend/
│   ├── manage.py
│   ├── config/
│   └── apps/
│       ├── users/
│       ├── conversations/
│       ├── messages/
│       ├── notifications/
│       └── attachments/
│
├── realtime_service/
│   └── ...
│
├── frontend/
│   └── ...
│
├── infrastructure/
│   └── ...
│
├── .env.example
├── .gitignore
├── pyproject.toml
└── README.md
```

## Tech Stack

### Backend

* Python
* Django
* Django REST Framework
* FastAPI
* PostgreSQL
* Redis
* Celery

### Infrastructure

* Docker
* Nginx
* GitHub Actions

### Frontend

* React / Next.js

## Features

Planned functionality:

* User registration and authentication
* Private conversations
* Group conversations
* Real-time messaging
* Online/offline status
* Typing indicators
* Message delivery and read status
* Message editing and deletion
* File and image attachments
* Notifications
* Message search
* Pagination
* Group member management

## Development

The project uses **Poetry** for dependency management.

Install dependencies:

```bash
poetry install
```

Run the Django development server:

```bash
poetry run python backend/manage.py runserver
```

## Environment Variables

Environment-specific and sensitive configuration is stored in `.env`.

The `.env` file is not committed to the repository.

Create a local `.env` file based on `.env.example` and configure the required variables.

Example:

```env
SECRET_KEY=your-secret-key
DEBUG=True

DB_NAME=messenger
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432
```

## Project Status

🚧 **Work in progress**

The project is currently in the initial development stage.

The basic project structure, Django backend, and core applications have been initialized. New functionality and services will be implemented progressively.
