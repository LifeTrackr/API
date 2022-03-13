import yaml
from sqlalchemy import Enum
import os
from definitions import ROOT_DIR

companion_events = os.path.join(ROOT_DIR, "api/types/companion_events.yaml")

def _unpack():
    with open(companion_events, "r") as stream:
        try:
            loaded = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            return exc
    return [Enum(*loaded[key], name=key) for key in loaded]

def get_companions():
    companion_names = [enum.name for enum in _unpack()]
    return Enum(*companion_names, name="companion_types")

def get_events():
    events = []
    for enum in _unpack():
        for event in enum.enums:
            events.append(event)
    return Enum(*events, name="event_types")

# get_companions("../types/companion_events.yaml")
print(get_events())