import os
import io
import shutil
import pathlib
import urllib.request
import zipfile
from crhelper import CfnResource
from pathlib import Path

helper = CfnResource()

AERIE_VERSION = "v1.0.1"


class EFS:
    aerie = Path("/mnt/efs/ait")
    aerie_filestore = aerie / "aerie"
    postgres = aerie / "postgres"
    deployment = aerie / "deployment"
    init_postgres = aerie / "init_postgres"
    init_hasura = aerie / "init_hasura"
    init_commanding = aerie / "init_commanding"


@helper.create
def clone_deployment(event, _):
    # Unsure why this is here - don't think we need to clean out /tmp on every invocation
    # if os.listdir("/tmp"):
    #     folder = "/tmp"
    #     for filename in os.listdir(folder):
    #         file_path = os.path.join(folder, filename)
    #         try:
    #             if os.path.isfile(file_path) or os.path.islink(file_path):
    #                 os.unlink(file_path)
    #             elif os.path.isdir(file_path):
    #                 shutil.rmtree(file_path)
    #         except Exception as e:
    #             print("Failed to delete %s. Reason: %s" % (file_path, e))

    url = f"https://github.com/NASA-AMMOS/aerie/releases/download/{AERIE_VERSION}/deployment.zip"
    filehandle = urllib.request.urlopen(url)
    with zipfile.ZipFile(io.BytesIO(filehandle.read())) as zipObj:
        # Extract all the contents of zip file in different directory
        zipObj.extractall("/tmp")

    # Create the required directory structure (one directory for each access point)
    EFS.aerie_filestore.mkdir(parents=True, exist_ok=True)
    EFS.postgres.mkdir(parents=True, exist_ok=True)
    EFS.deployment.mkdir(parents=True, exist_ok=True)
    EFS.init_postgres.mkdir(parents=True, exist_ok=True)
    EFS.init_hasura.mkdir(parents=True, exist_ok=True)
    EFS.init_commanding.mkdir(parents=True, exist_ok=True)

    # Copy relevant seed files into the appropriate directories for the
    #   ECS Tasks which will use them as a mounted volume
    shutil.copytree("/tmp/deployment", EFS.deployment, dirs_exist_ok=True)
    shutil.copytree("/tmp/deployment/postgres-init-db", EFS.init_postgres, dirs_exist_ok=True)
    shutil.copytree("/tmp/deployment/hasura/metadata", EFS.init_hasura, dirs_exist_ok=True)

    helper.Data["message"] = str(os.listdir("/mnt/efs/"))


@helper.delete
@helper.update
def no_op(_, __):
    return None


def handler(event, context):
    helper(event, context)
