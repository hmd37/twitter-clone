# Twitter Clone

![CI](https://github.com/hmd37/twitter-clone/actions/workflows/ci.yml/badge.svg)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/hmd37/twitter-clone)

A Twitter clone built with FastAPI, SQLAlchemy, and PostgreSQL.

## Stack
- FastAPI
- SQLAlchemy 2.0
- PostgreSQL
- Alembic
- JWT Auth
- Docker

## Run locally
cp .env.example .env
uvicorn app.main:app --reload

## Run with Docker
docker-compose up --build

## Run tests
pytest tests/ -v
