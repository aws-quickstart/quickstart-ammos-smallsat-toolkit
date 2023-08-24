import json
import re
import urllib.parse
from dataclasses import dataclass
from typing import Dict

import boto3

########################
##  Helper Functions  ##
########################


def safe_decode(string):
    """
    Input is a string that may or may not be URL encoded
    This function returns the string, as-is, if not URL encoded
    Returns decoded if is URL encoded
    """
    try_decode = urllib.parse.unquote(string)
    if len(string) > len(try_decode):
        return try_decode
    return string


def is_http(string):
    pattern = r"^http(s):\/\/.*"
    is_match = bool(re.match(pattern, string))
    return is_match


def is_s3(string):
    pattern = r"^s3:\/\/.*"
    is_match = bool(re.match(pattern, string))
    return is_match


def get_from_http(url):
    f = requests.get(url)
    return f.text


def get_from_s3(uri):
    bucket, file_key = uri.split("//")[1].split("/", maxsplit=1)
    s3_client = boto3.client("s3")
    obj = s3_client.get_object(Bucket=bucket, Key=file_key)
    content = json.loads(obj["Body"].read().decode("utf-8"))
    return content


def get_params_list_from_source(param_string):
    param_string = safe_decode(param_string)
    if is_http(param_string):
        content = get_from_http(param_string)
        return content

    if is_s3(param_string):
        content = get_from_s3(param_string)
        return content

    content = json.loads(param_string)
    return content




@dataclass
class Params:
    """
    The Params class contains helper scripts for converting Configurator outputs
    and Cloudformation inputs between different formats
    """

    params: Dict

    @staticmethod
    def get_dict_from_params_input_agnostic(params_input):
        params = Params.new_from_params_input_agnostic(params_input)
        params_dict = params.get_dict()
        return params_dict

    @staticmethod
    def new_from_params_input_agnostic(params_input):
        params_list = get_params_list_from_source(params_input)
        params = Params.load_from_list(params_list)
        return params

    @staticmethod
    def load_from_list(params_list):
        """
        Used in the above static method
        """
        params_dict = {k: v for k, v in (item.split("=") for item in params_list)}
        params = Params(params=params_dict)
        return params

    def get_dict(self):
        """
        Outputs dictionary representation of  parameters
        """
        return self.params

    def get_list(self):
        """
        Outputs JSON list representation of the parameters, example:
        [
            "key1=value1",
            "key2=value2",
            "key3=value3"
        ]
        """
        params_list = [f"{key}={value}" for (key, value) in self.params.items()]
        return params_list

    def get_query_string(self):
        """
        Outputs an url-encoded json.dump of the dictionary represenation of the params
        """
        json_string = json.dumps(self.get_list())
        encoded_json = urllib.parse.quote(json_string)
        return encoded_json
