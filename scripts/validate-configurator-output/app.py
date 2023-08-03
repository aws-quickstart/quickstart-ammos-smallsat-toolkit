from dataclasses import dataclass
import json

import cfn_flip

filename = "test.json"
with open(filename) as f:
    stuff = json.load(f)

def get_dict_from_params_list(params_list):
    params_keys = []
    for param in params_list:
        key, value = param.split('=')
        params_keys.append(key)
    return params_keys

params_list = get_dict_from_params_list(stuff)

filename = "ammos-cubs.main.template.yaml"

with open(filename) as f:
    template_raw = f.read()

template_flat_json = cfn_flip.to_json(template_raw)
template_dict = json.loads(template_flat_json)
template_keys = list(template_dict["Parameters"].keys())

diff_key = [key for key in template_keys if key not in params_list]
print(diff_key)

@dataclass
class ValidateParameters:
    stack_parameters: str
    file_parameters: str

