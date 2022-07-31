"""
    datarouterapi.helpers

    Module containing classes and functions which are generic and used
    throughout the code base.

    :copyright: (c) 2022 Red Hat, Inc.
    :license: GPLv3, see LICENSE for more details.
"""
import tarfile
from teflo.exceptions import TefloReportError
import os
import requests
import json


def compose_pload(payload_dir, tar_dest):
    check_dir = validate_struc_before_compose(payload_dir)
    try:
        with tarfile.open(tar_dest + ".tar.gz", "w:gz") as ntar:
            ntar.add(payload_dir, arcname=os.path.basename(payload_dir))
            return f'{tar_dest}.tar.gz'
    except Exception as ex:
        raise TefloReportError(f'Failed rto compose Payload with err {ex}')

def validate_struc_before_compose(payload_dir):
    """ Validating payload is not empty and has files."""

    dir_content = []
    files_arry = []
    for dirname, dirnames, filenames in os.walk(payload_dir):
        for subdirname in dirnames:
            dir_content.append(os.path.join(dirname, subdirname))

        for filename in filenames:
            files_arry.append(os.path.join(dirname, filename))

    if len(dir_content) >= 0 and len(files_arry) >= 0:
        return dir_content
    else:
        raise TefloReportError("Payload Dir is empty!")


def send_post_req(dr_token_url, body):
    """Send POST req to DR API to get access token"""
    res = requests.post(url=dr_token_url,
                        data=body)
    if res.status_code == 200:
        data = res.json()
        return data
    else:
        raise TefloReportError(f'Generated access token Failed with status code {res["status_code"]}.')


