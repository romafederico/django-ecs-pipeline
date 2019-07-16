import namedtupled
import json
import os


def get_config(env):
    env_folder = os.path.join(os.path.dirname(__file__), '..', '..', 'envs',  env)
    default_path = os.path.abspath(os.path.join(env_folder, "config.json"))

    if os.path.isfile(default_path):
        file = open(default_path)
        default_json = json.load(file)
        return namedtupled.map(default_json)

    return 'No JSON found'
