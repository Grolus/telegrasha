
import json


with open('config.json', 'r', encoding='utf-8') as file:
    cfg = json.load(file)

globals().update(cfg)
