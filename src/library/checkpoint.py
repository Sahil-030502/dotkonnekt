import json
import os

from src.utils.config import CHECKPOINT_DIR


def save_checkpoint(run_id, state):

    os.makedirs(CHECKPOINT_DIR, exist_ok=True)

    path = os.path.join(CHECKPOINT_DIR, f"{run_id}.json")

    with open(path, "w") as file:
        json.dump(state, file, indent=4)


def load_checkpoint(run_id):

    path = os.path.join(CHECKPOINT_DIR, f"{run_id}.json")

    if not os.path.exists(path):
        return None

    with open(path, "r") as file:
        return json.load(file)