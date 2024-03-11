import json
import signal

from flask import Blueprint, current_app, request

app_blueprint = Blueprint("app", __name__)


def timeout_handler(signum, frame):
    raise TimeoutError("Operation timed out")


@app_blueprint.route("/")
def hello():
    print("Hello, World!", flush=True)
    return "Hello, World!", 200


@app_blueprint.route("/read/<file_path>")
def read(file_path):
    lock = current_app.config["lock"]
    data = current_app.config["data"]
    if lock is None or data is None:
        return "Internal error", 500

    # Set up timeout handler to prevent deadlocks of the lock
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(1)

    try:
        # Wait for no other process to be writing the file and register the process with the lock
        while True:
            with lock:
                if data.get(file_path, 0) >= 0:
                    data[file_path] = data.get(file_path, 0) + 1
                    break

        try:
            with open(file_path, "r") as file:
                content = file.read()
                return content, 200
        except Exception as e:
            print(f"[ERROR] {e}", flush=True)
            return "Could not read file", 500
    except TimeoutError:
        return "Operation timed out", 500
    finally:
        # Cancel the alarm
        signal.alarm(0)

        # Unregister the process with the lock
        with lock:
            data[file_path] = data.get(file_path, 1) - 1


@app_blueprint.route("/write/<file_path>", methods=["POST"])
def write(file_path):
    lock = current_app.config["lock"]
    data = current_app.config["data"]
    if lock is None or data is None:
        return "Internal error", 500

    content = request.json
    if not content:
        return "No data provided", 400

    # Set up timeout handler to prevent deadlocks of the lock
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(1)

    try:
        # Wait for no other process to be reading the file and register the process with the lock
        while True:
            with lock:
                if data.get(file_path, 0) == 0:
                    data[file_path] = -1
                    break

        try:
            with open(file_path, "w") as file:
                file.write(json.dumps(content))
            return "OK", 200
        except Exception as e:
            print(f"[ERROR] {e}", flush=True)
            return "Could not write to file", 500
    except TimeoutError:
        return "Operation timed out", 500
    finally:
        # Cancel the alarm
        signal.alarm(0)

        # Unregister the process with the lock
        with lock:
            data[file_path] = 0
