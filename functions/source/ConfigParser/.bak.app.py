import re
import requests
import urllib

test_string = "lorem ipsum"
test_string = "https://developers.google.com/edu/python/regular-expressionso"

def safe_decode(string):
    try_decode = urllib.parse.unquote(string)
    if len(string) > len(try_decode):
        return try_decode
    return string

def is_http(string):
    pattern = r"^http(s):\/\/.*"
    is_match = bool(re.match(pattern,string))
    return is_match

def is_s3(string):
    pattern = r"^s3:\/\/.*"
    is_match = bool(re.match(pattern,string))
    return is_match

def get_from_http(url):
    f = requests.get(url)
    return f.text

def get_from_s3(uri):
    bucket = uri.split("//")[1].split('/')[0]
    key_list = uri.split("//")[1].split('/')[1:]
    key = "/".join(key_list)
    return key

def get_content(param_input):
    param_input = safe_decode(param_input)

    if is_http(param_input):
        return get_from_http(param_input)

    if is_s3(param_input):
        return get_from_s3(param_input)

    return param_input
