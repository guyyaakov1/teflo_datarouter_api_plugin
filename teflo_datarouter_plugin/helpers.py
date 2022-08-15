"""
    datarouterapi.helpers

    Module containing classes and functions which are generic and used
    throughout the code base.

    :copyright: (c) 2022 Red Hat, Inc.
    :license: GPLv3, see LICENSE for more details.
"""
import tarfile
from teflo.exceptions import TefloReportError
import shutil
import os
import requests
import json


def compose_pload(payload_dir, results_artufact_path, workspace):
    tar_dir_list = []
    check_dir = validate_struc_before_compose(payload_dir)
    with tarfile.open(payload_dir + ".tar.gz", "w:gz") as ntar:
        ntar.add(payload_dir, arcname=os.path.basename(payload_dir))
        for member in ntar.getmembers():
            tar_dir_list.append(member.name)
        shutil.copy2(f'{payload_dir}.tar.gz', f'{workspace}/{results_artufact_path}/')
        return tar_dir_list


def validate_compose_payload_content(tar_dir_list):
    pay_structer = ['/resultsdb', '/results/', '/attachments']
    for dir in pay_structer:
        get_dir_list = list(filter(lambda x: dir in x, tar_dir_list))
        if not get_dir_list:
            raise TefloReportError(f'Datarouter payload structer incorrect, missing dir name - {dir}')
    return "Validate payload successfully."


def validate_struc_before_compose(payload_dir):
    """ Validating payload contain results/ dir and is not empty."""

    dir_contenct = []
    for dirname, dirnames, filenames in os.walk(payload_dir):
        for subdirname in dirnames:
            dir_contenct.append(os.path.join(dirname, subdirname))

        for filename in filenames:
            dir_contenct.append(os.path.join(dirname, filename))
    if '/results/' not in dir_contenct:
        raise TefloReportError("Payload Dir structure is incorrect!")
    else:
        return True


def send_get_req(dr_token_url, body):
    res = requests.post(url=dr_token_url,
                        data=body)
    if res.status_code == 200:
        return res
    else:
        raise TefloReportError(f'Generated access token Failed with status code {res.status_code}.')


def get_token_sting(response):
    json_ac = json.loads(response.content.decode('utf8'))
    return json_ac['access_token']
