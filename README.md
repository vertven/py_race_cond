# Py Race Cond

## Description

Using a custom gunicorn app to setup a global variable "lock" for all workers to
share.

## Usage

```bash
docker-compose up
```

## Test

```bash
chmod +x race.sh
./race.sh
```

## Local Development

```bash
# Enter the virtual environment and install the dependencies
poetry shell
poetry install

# Run the app
python -m py_race_cond
```
