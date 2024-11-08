import os
import json

current_dir = os.path.dirname(__file__)

with open(os.path.join(current_dir, 'parts.json'), 'r') as f:
    PARTS = json.load(f)
with open(os.path.join(current_dir, 'submit_values.json'), 'r') as f:
    SUBMIT_VALUES = json.load(f)