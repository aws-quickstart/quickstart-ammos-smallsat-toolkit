# Role Checker

This slim function will check the deployment account for a set of required IAM Roles and indicate in the Outputs whether they already exist. This allows the main deployment to skip creation of IAM Roles if they have been pre-deployed and grants improved deployment flexibility in accounts with restrictive IAM policies.
