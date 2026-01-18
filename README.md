# Testudo CMSC414 Seat Checker

Checks CMSC414 sections on Testudo and sends a Pushover notification when new sections have open seats.

## Local Setup (Windows)

1. Create a virtual environment (optional but recommended):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

3. Create a `.env` file in the project root with:

```
PUSHOVER_TOKEN=your_pushover_app_token
PUSHOVER_USER=your_pushover_user_key
```

4. Run the checker:

```powershell
& .\.venv\Scripts\python.exe check_seats.py
```

## Notes
- The script loads environment variables via `python-dotenv` (`load_dotenv()`), so `.env` is used locally.
- It tracks open section IDs in `seats_state.txt` and only notifies when new sections open compared to the last run.

## GitHub Actions / CI
`.env` files are not used in GitHub Actions. Set secrets in the repository settings and expose them as environment variables in the workflow.

Example step:

```yaml
env:
  PUSHOVER_TOKEN: ${{ secrets.PUSHOVER_TOKEN }}
  PUSHOVER_USER: ${{ secrets.PUSHOVER_USER }}
```

Then run:

```yaml
- name: Run seat checker
  run: |
    python -m pip install -r requirements.txt
    python check_seats.py
```

## Scheduling
- Locally: use Windows Task Scheduler to run `check_seats.py` periodically.
- In CI: use a scheduled workflow (`on: schedule`) with a cron expression.
