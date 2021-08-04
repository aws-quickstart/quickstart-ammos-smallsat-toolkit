import sys
import cfnresponse
import boto3
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    responseData = {}

    try:
        logger.info("Received event: {}".format(json.dumps(event)))
        result = cfnresponse.FAILED
        client = boto3.client("cognito-idp")

        # Pull identifiers from the request (passes as Properties in the custom resource)
        user_pool_id = event["ResourceProperties"]["UserPoolId"]
        client_id = event["ResourceProperties"]["ClientId"]

        if event["RequestType"] in ["Create", "Update"]:
            # Describe the User Pool Client to extract client secret
            response = client.describe_user_pool_client(
                UserPoolId=user_pool_id,
                ClientId=client_id,
            )
            props = response["UserPoolClient"]

            # Add ClientSecret to the custom resource attributes (Fn::GetAtt)
            responseData["ClientSecret"] = props["ClientSecret"]

            result = cfnresponse.SUCCESS
        elif event["RequestType"] == "Delete":
            logger.info("Delete request - NOOP")
            result = cfnresponse.SUCCESS

    except Exception as e:
        logger.error("Error: {}".format(e))
        result = cfnresponse.FAILED

    logger.info("Returning response of: {}, with result of: {}".format(
        result, responseData))
    sys.stdout.flush()
    # https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-lambda-function-code-cfnresponsemodule.html
    cfnresponse.send(event, context, result, responseData)
