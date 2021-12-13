import json
import os


PREF_PATH = os.path.expanduser("~/pluck.json")


def load_preferences():
    if not os.path.exists(PREF_PATH):
        return {}
    with open(PREF_PATH, 'r') as f:
        try:
            return json.load(f)
        except json.decoder.JSONDecodeError:
            return {}


def get_preference(name, default=None):
    return load_preferences().get(name, default)


def save_preference(name, value):
    preferences = load_preferences()
    preferences[name] = value
    with open(PREF_PATH, 'w') as f:
        json.dump(preferences, f)

