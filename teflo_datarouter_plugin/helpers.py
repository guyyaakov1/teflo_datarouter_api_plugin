"""
    datarouterapi.helpers

    Module containing classes and functions which are generic and used
    throughout the code base.

    :copyright: (c) 2022 Red Hat, Inc.
    :license: GPLv3, see LICENSE for more details.
"""
import tarfile
import os
from teflo.exceptions import TefloReportError
import shutil
import os


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
    pay_structer = ['/resultsdb', '/results', '/attachments']
    for dir in pay_structer:
        get_dir_list = list(filter(lambda x: dir in x, tar_dir_list))
        if not get_dir_list:
            raise TefloReportError(f'Datarouter payload structer incorrect, missing dir name - {dir}')
    return "Validate payload successfully."


def validate_struc_before_compose(payload_dir):
    dir_contenct = []
    for dirname, dirnames, filenames in os.walk(payload_dir):
        for subdirname in dirnames:
            dir_contenct.append(os.path.join(dirname, subdirname))

        for filename in filenames:
            dir_contenct.append(os.path.join(dirname, filename))

    if len(dir_contenct) <= 3:
        raise TefloReportError("Payload Dir is empty!")

    return True
