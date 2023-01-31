import logging
import secrets
import string
import random

import boto3
import botocore

import cfnresponse

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def rand_seq(seq, at_least: int, at_most: int) -> list:
    n = secrets.choice(range(at_least, at_most + 1))
    return [secrets.choice(seq) for _ in range(n)]


def make_password(length: int) -> str:
    length = max(length, 18)  # At least 18 chars
    password = []
    password += rand_seq(string.punctuation, 1, 3)
    password += rand_seq(string.digits, 1, 3)
    password += rand_seq(string.ascii_uppercase, 3, 9)
    n = length - len(password)
    password += rand_seq(string.ascii_lowercase, n, n)
    random.shuffle(password)
    return "".join(password)


def lambda_handler(event, context):
    """Lambda Handler for dealing with creating a new cognito user using AWS Cognito

    Args:
        event (dict): Event dictionary from custom resource
        context (obj): Context manager
    """

    user_pool_id = event["ResourceProperties"]["UserPoolId"]
    username = "admin"

    # Generate random word using secrets for 20 characters long
    password = make_password(20)

    responseData = {}
    status = cfnresponse.FAILED
    if event["RequestType"] == "Create":
        # Run in the cloud to make cognito user
        client = boto3.client("cognito-idp")

        try:
            client.admin_create_user(
                UserPoolId=user_pool_id, Username=username, TemporaryPassword=password
            )

            responseData["Username"] = username
            responseData["TemporaryPassword"] = password

            # Send response back with CIDP Response to CFN
            status = cfnresponse.SUCCESS

        except botocore.exceptions.ClientError as error:
            logger.error("Error: {}".format(error))
            responseData = {"Error": error.response["Error"]}
    elif event["RequestType"] in ["Delete", "Update"]:
        # No action needs to be taken for delete or update events
        status = cfnresponse.SUCCESS
    else:
        responseData = {"Message": "Invalid Request Type"}

    cfnresponse.send(event, context, status, responseData)
