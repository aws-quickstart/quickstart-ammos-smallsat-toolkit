import sys
import os
import cfnresponse
import boto3
import botocore
import json
import logging

logger = logging.getLogger()
logger.setLevel(os.getenv("LOG_LEVEL", "DEBUG"))


def lambda_handler(event, context):
    try:
        logger.debug("Received event: {}".format(json.dumps(event)))
        result = cfnresponse.FAILED
        client = boto3.client("iam")

        # Pull identifiers from the request (passes as Properties in the custom resource)
        role_names = event["ResourceProperties"].get("RoleNames", [])
        role_arns = {}

        if event["RequestType"] in ["Create", "Update"]:
            for name in role_names:
                try:
                    logger.debug(f"Checking Account Roles for {name}")
                    arn = client.get_role(RoleName=name)["Role"]["Arn"]
                    logger.debug(f"Role already exists: {arn}")
                    role_arns[name] = arn
                except botocore.exceptions.ClientError as e:
                    if e.response["Error"]["Code"] == "NoSuchEntity":
                        logger.debug(f"{name} Role does not exist")
                        role_arns[name] = "NA"
                    else:
                        logger.error("Uncaught boto exception", e)
            result = cfnresponse.SUCCESS
        elif event["RequestType"] == "Delete":
            logger.info("Delete request - NOOP")
            result = cfnresponse.SUCCESS

    except Exception as e:
        logger.error("Error: {}".format(e))
        result = cfnresponse.FAILED
    responseData = role_arns
    logger.info("Returning response of: {}, with result of: {}".format(
        result, responseData))
    sys.stdout.flush()
    # https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-lambda-function-code-cfnresponsemodule.html
    cfnresponse.send(event, context, result, responseData)
