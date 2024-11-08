demo:
	uv run alembic upgrade head
	uv run python -m bytewax.run uptime.dataflows
	uv run uvicorn uptime.app:app
