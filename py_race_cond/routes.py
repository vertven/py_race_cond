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


@app_blueprint.route("/read")
def read():
    lock = current_app.config["lock"]

    # Register the process with the lock
    with lock.get_lock():
        lock.value += 1

    try:
        with open("data.json", "r") as file:
            data = file.read()

            # Release the lock
            with lock.get_lock():
                lock.value -= 1

            return data, 200
    except Exception as e:
        print(f"[ERROR] {e}", flush=True)
        return "Could not read file", 500


@app_blueprint.route("/write", methods=["POST"])
def write():
    lock = current_app.config["lock"]

    data = request.json
    if not data:
        return "No data provided", 400

    # Set up timeout handler to prevent deadlocks of the lock
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(1)

    try:
        while True:
            # Get the lock
            with lock.get_lock():
                # Check if the lock is available (no other process is using it)
                if lock.value > 0:
                    continue

                try:
                    with open("data.json", "w") as file:
                        file.write(json.dumps(data))
                    return "OK", 200
                except Exception as e:
                    print(f"[ERROR] {e}", flush=True)
                    return "Could not write to file", 500
    except TimeoutError:
        return "Operation timed out", 500
    finally:
        # Cancel the alarm
        signal.alarm(0)
