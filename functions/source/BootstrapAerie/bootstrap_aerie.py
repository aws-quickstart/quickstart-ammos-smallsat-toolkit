import io
import os
import shutil
import tarfile
import urllib.request
import zipfile
from pathlib import Path

from crhelper import CfnResource

helper = CfnResource()

AERIE_VERSION = "v1.4.0"


class EFS:
    aerie = Path("/mnt/efs/aerie")
    aerie_filestore = aerie / "filestore"
    postgres = aerie / "postgres"
    deployment = aerie / "deployment"
    init_postgres = aerie / "init_postgres"
    init_hasura = aerie / "init_hasura"


@helper.create
def clone_deployment(event, _):
    aerie_version = event["ResourceProperties"].get("AerieVersion", AERIE_VERSION)

    url = f"https://github.com/NASA-AMMOS/aerie/releases/download/{aerie_version}/Deployment.zip"
    filehandle = urllib.request.urlopen(url)
    with zipfile.ZipFile(io.BytesIO(filehandle.read())) as zipObj:
        # Extract all the contents of zip file in different directory
        zipObj.extractall("/tmp")

    with tarfile.open("/tmp/deployment.tar") as tar:
        tar.extractall("/tmp")

    # Create the required directory structure (one directory for each access point)
    EFS.aerie_filestore.mkdir(parents=True, exist_ok=True)
    EFS.postgres.mkdir(parents=True, exist_ok=True)
    EFS.deployment.mkdir(parents=True, exist_ok=True)
    EFS.init_postgres.mkdir(parents=True, exist_ok=True)
    EFS.init_hasura.mkdir(parents=True, exist_ok=True)

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
