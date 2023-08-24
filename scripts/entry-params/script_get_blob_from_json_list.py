import json

from params import Params

with open("main-entry.json", "r") as f:
    params_json_list = json.load(f)

params = Params.load_from_list(params_json_list)
blob = params.get_query_string()
print(blob)
