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
        result = cfnresponse.SUCCESS
        reason = None
        client = boto3.client("iam")

        # Pull identifiers from the request (passes as Properties in the custom resource)
        role_names = event["ResourceProperties"].get("RoleNames", [])
        role_arns = {}
        missing_roles = []

        if event["RequestType"] in ["Create", "Update"]:
            for name in role_names:
                key = "-".join(name.split("-")[-1:])  # Strip the leading ProjectName from role name
                try:
                    logger.debug(f"Checking Account Roles for {name}")
                    role = client.get_role(RoleName=name)["Role"]
                    role_arn = role["Arn"]
                    logger.debug(f"Role already exists: {role_arn}")
                    role_arns[key + "Arn"] = role_arn
                    role_arns[key + "Name"] = role["RoleName"]
                except botocore.exceptions.ClientError as e:
                    if e.response["Error"]["Code"] in ["NoSuchEntity", "AccessDenied"]:
                        logger.error(f"{name} Role does not exist")
                        # The roles should be deployed all at once or not at all (via the supplied template);
                        #  therefore, it does not make sense to proceed with the deployment if one of them is missing
                        result = cfnresponse.FAILED
                        missing_roles.append(name)
                    else:
                        logger.error("Uncaught boto exception", e)
                        result = cfnresponse.FAILED
        elif event["RequestType"] == "Delete":
            logger.info("Delete request - NOOP")
            result = cfnresponse.SUCCESS

    except Exception as e:
        logger.error("Error: {}".format(e))
        result = cfnresponse.FAILED

    responseData = role_arns
    if result == cfnresponse.FAILED:
        reason = ("Required roles were not found in account; please use or refer to the ast-iam-role template for a "
                  "list of required roles. The following roles were not found: " + ", ".join(missing_roles))
    logger.info("Returning response of: {}, with result of: {}".format(result, responseData))
    sys.stdout.flush()
    # https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-lambda-function-code-cfnresponsemodule.html
    cfnresponse.send(event, context, result, responseData, reason=reason)
