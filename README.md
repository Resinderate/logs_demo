# Logs Demo - Uptime

Demo app processing some request info and exposing stats via API.

## Python / Environment

- Uses `uv` for sorting Python and Virtualenv. Can be installed here: https://github.com/astral-sh/uv?tab=readme-ov-file#installation
- All project commands run with `uv run ...` to automatically install needed python versions / virtual environment / dependencies as needed (and when changed).

## Demo

Some pieces of setup here.
- `uv run alembic upgrade head` to run migrations and create local DB. Here just using SQLite for simplicity.
    - To clear the DB and data just delete the `uptime.db` file created in the root folder and re-run the migrations to create the DB again.
- `uv run python -m bytewax.run uptime.dataflows` to process the log file and write the results to the DB.
- `uv run uvicorn uptime.app:app` to run the API with uvicorn.

As long as we have `uv` we don't need to install Python, virtualenv, or it's dependencies.

Those can be **run with a single** command via make:
- `make demo`

The API will then be running with available data. For example, and can then be queried with:
```
$ make demo
uv run alembic upgrade head
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
uv run python -m bytewax.run uptime.dataflows
uv run uvicorn uptime.app:app
INFO:     Started server process [30978]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)


GET http://127.0.0.1:8000/api/customers/cust_15/stats?from=2024-11-05
->
{
  "id": 171,
  "created_at": "2024-11-08T13:19:18",
  "updated_at": "2024-11-08T13:19:18",
  "customer": "cust_15",
  "from_date": "2024-11-05",
  "total_requests": 5,
  "failed_requests": 2,
  "successful_requests": 3,
  "uptime": 0.6,
  "average_latency_ms": 973,
  "median_latency_ms": 1153,
  "p99_latency_ms": 1665
}
```

## Organisation

Split into some components:
- `models.py` for data models / db schema. Declaritively via SQLAlchemy.
- `routes.py` for API routes via FastAPI
- `schemas.py` for schema communicated over those routes. With Pydantic.
- `stores.py` for handling saving / fetching model data.
- `dataflows.py` for logic to consume stream of logs. With Bytewax.
- `/migrations` for describing migrations to create DB Schema via Alembic.
- `/data` for local source of logs.


## Tools

Linting / formatting with `ruff`.

```
uv run ruff format
uv run ruff check
```

Typechecking with `mypy`.
```
uv run mypy
```

Run tests with `pytest`
```
uv run pytest
```

## Notes

- There didn't seem to be wheels available for `bytewax` on Python 3.12 or 3.13, and didn't seem to build correctly on my M1 Pro. So used 3.11 instead.
