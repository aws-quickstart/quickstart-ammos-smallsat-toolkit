import json
import logging
import os

import boto3

from crhelper import CfnResource
from params import Params

logger = logging.getLogger(__name__)
LOGLEVEL = os.getenv("LOGLEVEL", logging.DEBUG)
logger.setLevel(LOGLEVEL)

helper = CfnResource(
    json_logging=False,
    log_level=os.getenv("LOG_LEVEL", "DEBUG"),
    boto_level="CRITICAL",
    sleep_on_delete=120,
    ssl_verify=None,
)


@helper.create
@helper.update
def parse_config(event, _):
    try:
        raw_params = event["ResourceProperties"]["MainStackParams"]
    except KeyError:
        logging.error(
            "Expect entry vars to be passed as 'MainStackParams' in 'ResourceProperties'"
        )

    params_dict = Params.get_dict_from_params_input_agnostic(raw_params)
    helper.Data.update(**params_dict)
    return None


@helper.delete
def no_op(_, __):
    return None


def handler(event, context):
    helper(event, context)
