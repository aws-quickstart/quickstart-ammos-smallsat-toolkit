import os
import io
import shutil
import subprocess
import pathlib
import urllib.request
import zipfile
import tarfile
from crhelper import CfnResource

helper = CfnResource()

@helper.create
@helper.update
def clone_deployment(event, _):
    if os.listdir("/tmp"):
        folder = '/tmp'
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))

    url = 'https://github.com/NASA-AMMOS/aerie/releases/download/v0.12.3/deployment.zip'
    filehandle = urllib.request.urlopen(url)
    with zipfile.ZipFile(io.BytesIO(filehandle.read())) as zipObj:
        # Extract all the contents of zip file in different directory
        zipObj.extractall('/tmp')


    pathlib.Path("/mnt/efs/aerie").mkdir(parents=True, exist_ok=True)
    pathlib.Path("/mnt/efs/postgres").mkdir(parents=True, exist_ok=True)
    pathlib.Path("/mnt/efs/deployment").mkdir(parents=True, exist_ok=True)
    pathlib.Path("/mnt/efs/init_postgres").mkdir(parents=True, exist_ok=True)
    pathlib.Path("/mnt/efs/init_hasura").mkdir(parents=True, exist_ok=True)

    shutil.copytree("/tmp/deployment", "/mnt/efs/deployment", dirs_exist_ok=True)
    shutil.copytree("/tmp/deployment/postgres-init-db", "/mnt/efs/init_postgres", dirs_exist_ok=True)
    shutil.copytree("/tmp/deployment/hasura/metadata", "/mnt/efs/init_hasura", dirs_exist_ok=True)

    helper.Data['message'] = str(os.listdir("/mnt/efs/"))
@helper.delete
def no_op(_, __):
    pass

def handler(event, context):
    helper(event, context)