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
An APIZIT local scan currently stops at unsupported framework detection; record
that result honestly. Future hosted qualification must use disposable dev resources
and exact commits after the platform gains an adapter. Production and real payments
are outside this fixture's scope.
