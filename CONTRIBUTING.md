# Contributing

Keep the common HTTP contract and mirror identity intact. Work on a `codex/` branch.

```sh
ruff check .
ruff format --check .
python manage.py check
pytest -q
python -c "from config.wsgi import application; assert application is not None"
```

CI exercises the same checks without cloud credentials. Never download model weights
in normal CI. Record local HTTP smoke results and the exact published commit.
Hosted qualification uses disposable APIZIT dev resources and exact commits; record
the measured scan and HTTP results. Follow the qualification evidence linked in the
README. Production and real payments are outside this fixture's scope.
