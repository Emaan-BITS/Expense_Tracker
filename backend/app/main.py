"""App entry point.

Routers are discovered, not listed: adding a feature means adding a folder
under app/features/, with no edit to this file.

In production this also serves the built React frontend, so the whole app is a
single process on a single port.
"""

import importlib
import pkgutil
from pathlib import Path

from fastapi import APIRouter, FastAPI
from fastapi.staticfiles import StaticFiles

from app import features
from app.core.db import get_conn, init_db

app = FastAPI(title="Expense Tracker")

init_db()


def _seed_if_empty() -> None:
    """Populate the database on first boot.

    Free hosting has an ephemeral disk, so every redeploy starts with nothing.
    An empty table looks like a broken app rather than a new one.
    """
    try:
        with get_conn() as conn:
            count = conn.execute("SELECT COUNT(*) FROM expenses").fetchone()[0]
        if count == 0:
            from seed import seed

            seed()
    except Exception as exc:  # never let seeding stop the app from starting
        print(f"skipped seeding: {exc}")


_seed_if_empty()

# Every package under app/features/ is expected to expose a `router` module.
for mod_info in pkgutil.iter_modules(features.__path__):
    if not mod_info.ispkg:
        continue
    module = importlib.import_module(f"app.features.{mod_info.name}.router")
    router = getattr(module, "router", None)
    if isinstance(router, APIRouter):
        app.include_router(router, prefix="/api")


@app.get("/api/health", tags=["meta"])
def health() -> dict[str, str]:
    return {"status": "ok"}


# Must stay last: a mount on "/" matches everything, so it would shadow the API
# routes above if it were registered first.
#
# In development this directory doesn't exist and Vite serves the frontend
# instead, so the mount is simply skipped.
#
# html=True serves index.html for "/" itself. It does NOT rewrite arbitrary
# unknown paths to index.html — /nonsense is still a 404. That's fine here:
# the tabs are React state, not URLs, so "/" is the only address the app has.
# A client-side router would need a catch-all route added below.
DIST = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if DIST.is_dir():
    app.mount("/", StaticFiles(directory=DIST, html=True), name="ui")
