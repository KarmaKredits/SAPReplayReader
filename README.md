
# SAPReplayReader

Minimal scaffold for the SAPReplayReader Python project.

This project provides utilities to read and analyze SAP replay files and
includes a small API client to download replay JSON when authorized.

Quick start (Windows PowerShell)

1. Create and activate a virtual environment:

```powershell
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
```

If you need a specific Python version (example: Python 3.8+), create the
venv with the desired interpreter (replace the path or use the py launcher):

```powershell
# Use the py launcher to pick a specific Python: py -3.9 -m venv .venv
# Or point to an absolute interpreter: C:\\Python39\\python.exe -m venv .venv
```

2. Install dependencies and run tests:

```powershell
pip install -r requirements.txt
pytest -q
```

Notes on Python versions

- The project is compatible with multiple Python versions. The workspace
	virtualenv used while developing this scaffold is Python 3.7.9 and the
	pinned dependencies in `requirements.txt` (for example `pandas==1.3.5` and
	`pytest==6.2.5`) are selected to work with that interpreter.
- If you have Python 3.8+ installed, you can recreate the venv with that
	interpreter and then install the requirements; you may also upgrade
	`pandas`/`pytest` to newer releases if desired.

Environment variables and .env

- API credentials are read from environment variables by the API client.
	Common env names:
	- `SAP_EMAIL` or `SAPEMAIL`
	- `SAP_PASS` or `SAPPASS`
	- `SAPAUTH` (Bearer token used by `download_replay`)
- You can store these in a `.env` file and the project uses `python-dotenv`
	to load them automatically when running the code.

Running the package

You can run the package entrypoint (simple CLI) with:

```powershell
python -m sapreplayreader
```

Files created by scaffold:
- `src/sapreplayreader/` - package source
- `tests/` - basic pytest tests
- `requirements.txt` - runtime/test deps

The replay system and API client are intentionally left as implemented — do
not change the replay download logic unless you want to extend or replace it.
