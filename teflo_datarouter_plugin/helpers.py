"""
    datarouterapi.helpers

    Module containing classes and functions which are generic and used
    throughout the code base.

    :copyright: (c) 2022 Red Hat, Inc.
    :license: GPLv3, see LICENSE for more details.
"""
import time
import tarfile
from teflo.exceptions import TefloReportError, TefloError
from logging import getLogger
import os
import requests
import json

LOG = getLogger(__name__)


def validate_compose_payload_content(tar_dir_list):
    pay_structer = ['/resultsdb', '/results/', '/attachments']
    for dir in pay_structer:
        get_dir_list = list(filter(lambda x: dir in x, tar_dir_list))
        if not get_dir_list:
            raise TefloReportError(f'Datarouter payload structer incorrect, missing dir name - {dir}')
    return "Validate payload successfully."


def get_oauth_token(dr_token_url, dr_client_id, dr_client_secret):
    """GET TOKEN TO AUTH USER
    """
    body = {
            'grant_type': 'client_credentials',
            'client_id': dr_client_id,
            'client_secret': dr_client_secret,
            'scope': 'openid',
        }
    try:
        dr_token_req = send_post_req(dr_token_url=dr_token_url, body=body)
        LOG.debug('Successfully Generated access token from DR API.')
        return dr_token_req['access_token']
    except Exception as ex:
        raise TefloError(f'Generating access token from DR API Failed with error: {ex}')


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
        raise TefloReportError(f'Generated access token Failed with status code {res.status_code}.')


def get_req_status(get_url, ac_token, dr_client_id, dr_client_secret, dr_token_url, req_count=0):
    """Get Status of req. In case of 'PENDING' wait 5 min."""

    headers = {'Authorization': f'Bearer {ac_token}',
               'X-DataRouter-Auth': 'openid-connect-client-credentials-grant',
               }
    res = requests.get(url=get_url,
                       headers=headers, verify=False)
    if res.status_code == 401:
        res = handle_token_retry(req_count, dr_token_url, dr_client_id, dr_client_secret, get_url)

    if res.status_code == 200:
        json_content = json.loads(res.content.decode('utf8'))
        if json_content.get('status') == 'PENDING':
            while (json_content.get('status') != 'OK') and (json_content.get('status') != 'FAILURE')\
                    and (req_count <= 10):
                LOG.debug(f"Req status is {json_content['status']}. checking again in 30 sec. attempt -"
                          f" {req_count + 1}/10")
                time.sleep(30)
                res = requests.get(url=get_url,
                                   headers=headers, verify=False)
                json_content = json.loads(res.content.decode('utf8'))
                req_count = req_count + 1

                if res.status_code == 401:
                    res = handle_token_retry(req_count, dr_token_url, dr_client_id, dr_client_secret, get_url)
                    json_content = json.loads(res.content.decode('utf8'))

        if json_content["status"] == 'OK':
            LOG.info("Data sent successfully. For more info use log-level debug")
            LOG.debug(f'Req ID: {json_content["request_id"]} Status: {json_content["status"]}')
            # GET TARGET RESULTS
            for k, v in json_content['targets'].items():
                LOG.debug(f'Target Name: {k} Status: {v["status"]}')
            return json_content
        elif json_content["status"] == 'FAILURE':
            raise TefloReportError(f'req with id {json_content["request_id"]} failed')
            # return json_content
        elif json_content["status"] == 'PENDING':
            raise TefloReportError(f'Teflo DR plugin failed getting status of req with id: {json_content["request_id"]}'
                                   f' ,max wait to response is 5min. Please visit host url get status.')
        else:
            raise TefloReportError(f'Get request status Failed with status {json_content["status"]}.')
    else:
        raise TefloReportError(f'Get request status Failed with status code {res.status_code}.')


def handle_token_retry(req_count, dr_token_url, dr_client_id, dr_client_secret, get_url):
    LOG.info(f'Unauthorized: Signature has expired, Creating new token and trying again. attempt -'
             f' {req_count + 1}/10.')
    gen_ntoken = get_oauth_token(dr_token_url, dr_client_id, dr_client_secret)
    headers = {'Authorization': f'Bearer {gen_ntoken}',
               'X-DataRouter-Auth': 'openid-connect-client-credentials-grant',
               }
    res = requests.get(url=get_url,
                       headers=headers, verify=False)
    return res
