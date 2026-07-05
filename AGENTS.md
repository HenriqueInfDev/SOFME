# AGENTS

Purpose: Provide concise instructions for AI coding agents working on this repository, with emphasis on account/auth workflows.

## Quick Commands

- **Install deps:**

```
pip install -r requirements.txt
```
- **Run app:**

```
python main.py
```
- **Run tests (all):**

```
python run_tests.py
# or
pytest -q
```
- **Run auth/account tests:**

```
pytest tests/test_auth.py tests/test_user_edit.py -q
# or, use the project's test runner to filter by category when available:
python run_tests.py --category auth
```

## Account / Authentication Notes

- **Auth service:** [app/auth/service.py](app/auth/service.py) — central authentication and user CRUD logic; prefer modifying behavior here and keep UI thin.
- **Login UI:** [app/auth/login_window.py](app/auth/login_window.py) — UI glue; changes here should be minimal and covered by integration tests.
- **User management UI:** [app/auth/ui_user_window.py](app/auth/ui_user_window.py) — user create/edit dialogs.
- **Database:** [app/database/db.py](app/database/db.py) — DB initialization and helpers used by tests; use this to reset/init DB state for test runs.
- **Local params:** `local_params.txt` stores last-login and other local settings; avoid committing sensitive changes here.
- **Tests to run after changes:** [tests/test_auth.py](tests/test_auth.py), [tests/test_user_edit.py](tests/test_user_edit.py).

## Conventions & Best Practices for Agents

- **Feature layout:** Code is organized under `app/<feature>/` with `service.py`, repositories (`*_repository.py`), and `ui_*.py` for UI.
- **UI framework:** PySide6; prefer small UI edits and keep logic in `service.py`.
- **Testing:** Run related tests locally after edits; use `run_tests.py` for the project's test orchestration.
- **DB changes:** If altering schema, update tests and DB init in [app/database/db.py](app/database/db.py) and run full test suite.
- **Safety:** Do not remove or rename the default/support user account (`SUPORTE`) without explicit approval — many tests and local flows expect it.

## Next Suggested Customizations

- Create a small agent skill that runs the auth tests and opens failing test traces, e.g., `/run-auth-tests`.
- Add a short `CONTRIBUTING.md` section about local DB reset and test workflow, then link it from here.

---
Generated for AI agents to speed onboarding and edits in the account/auth area.
