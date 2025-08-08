# Run
```shell
flask --app flask_app.py --debug run
```

# How to use

Local env: copy .env.example to .env and set values (Windows CMD shows env differently; for PythonAnywhere set on the dashboard).
Build CSS:
```shell
npm run build:css
```
For dev: 
```shell
npm run watch:css
```
Optional: install pre-commit and set up hooks (run in a terminal):
```shell
pre-commit install
```
Push to GitHub to see CI run (lint + format check + tests).