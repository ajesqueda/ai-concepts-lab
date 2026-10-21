# ai-concepts-lab

Small demos of computer systems and AI concepts that I've rebuilt in my own words
while doing an MS in Computer Science and AI at Boston University. Each one is a
runnable example with tests, written to make one idea concrete.

These are my own concept demos. They are not course assignments or solutions.

## Index

| Topic | What it shows | Source |
|-------|---------------|--------|
| [Toy CPU](toy-cpu/) | The fetch-decode-execute cycle: a C `while` loop run as machine instructions, step by step | CX651 Week 1 |

## Run it

```bash
pip install -r requirements-dev.txt
ruff check .
pytest
```

## Workflow

Work happens on `feat/*` branches off `dev`, then is promoted `dev` → `qa` → `main`
through pull requests. CI runs ruff and pytest on every PR.
