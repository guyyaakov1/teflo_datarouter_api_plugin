# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Red Hat, Inc.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
"""
    datarouterapi_importer

    datarouter API importer module to connect to DataRouter API via Teflo. This class contains all the necessary
    classes and functions to import logs via datarouter service.

    :copyright: (c) 2022 Red Hat, Inc.
    :license: GPLv3, see LICENSE for more details.
"""
import requests
from teflo.core import ImporterPlugin
from teflo.helpers import schema_validator, gen_random_str
import json
import os
import tarfile
from teflo.exceptions import TefloReportError, TefloError
import re
from .helpers import validate_compose_payload_content, compose_pload, send_get_req, get_token_sting


class DataRouterPlugin(ImporterPlugin):

    __plugin_name__ = 'datarouter'
    __schema_file_path__ = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                        "files/schema.yml"))
    __schema_ext_path__ = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                       "files/schema_extensions.py"))

    def __init__(self, report):
        super(DataRouterPlugin, self).__init__(report)
        # creating logger for this plugin to get added to teflo's loggers
        self.create_logger(name='teflo_datarouter_plugin', data_folder=self.data_folder)

    def import_artifacts(self):
        """this method sends the data to the datarouter api and send results back to user.
        """
        payload_dir = os.path.join(self.data_folder,
                                   self.report_name)
        jconfig_dir = self.config['WORKSPACE']
        tar_payload = self.get_payload_dir(payload_dir)
        json_config_file = self.get_json_config_file(jconfig_dir)
        dr_token_url = self.provider_credentials['auth_url']
        dr_url = self.provider_credentials['host_url'] + '/api/results'

        # Get access Token
        ac_token = self.get_oauth_token(dr_token_url)

        # SEND PUT REQ AND RETURN TRACK ID
        results["request_uuid"] = self.send_put_req(dr_url, ac_token, tar_payload, json_config_file)

        return results

    def get_oauth_token(self, dr_token_url):
        """GET TOKEN TO AUTH USER
        """
        dr_client_id = self.provider_credentials['dr_client_id']
        dr_client_secret = self.provider_credentials['dr_client_secret']

        body = {
                'grant_type': 'client_credentials',
                'client_id': dr_client_id,
                'client_secret': dr_client_secret,
                'scope': 'openid',
            }
        try:
            dr_token_req = send_get_req(dr_token_url=dr_token_url, body=body)
            dr_token_srt = get_token_sting(response=dr_token_req)
            self.logger.debug('Successfully Generated access token from DR API.')
            return dr_token_srt
        except Exception as ex:
            raise TefloError(f'Failed Sending POST req with error: {ex}')

    def send_put_req(self, dr_url, access_token, tar_payload, json_config_file):
        """COLLECT DATA AND SEND PUT REQ TO SERVER"""
        headers = {'Authorization': f'Bearer {access_token}',
                   'X-DataRouter-Auth': 'openid-connect-client-credentials-grant',
                   }
        try:
            compose_payload = open(tar_payload['path'], 'rb')
            compose_config = open(json_config_file, 'rb')
            res = requests.put(url=dr_url,  headers=headers, files=[
                    ("metadata", compose_config),
                    ("payload", compose_payload)
                ], verify=False)
            if res.status_code == 200:
                self.logger.info('Data send successfully ro DR API.')
                j_res = json.loads(res.content.decode("utf-8"))
                self.logger.info(f'{j_res}')
                get_regex = self.get_token_regex(j_res)
                return get_regex
            else:
                raise TefloReportError(f'PUT req has Failed with err  {res.content}.')
        except Exception as ex:
            raise TefloReportError(f'Failed Sending PUT req with error: {ex}')

    def get_payload_dir(self, payload_dir):
        """Get provided datarouter payload and check if need to compose to '.tar.gz'.
        """
        # CHECK IF PAYLOAD EXIST IN ARTIFACTS
        if self.artifacts:
            payload_dir = self.artifacts[0]

        if self.report_name.endswith('.tar.gz') \
                and os.path.exists(payload_dir):
            self.logger.debug(f"Found valid payload {payload_dir}")
            return {"path": payload_dir}
        elif os.path.isdir(payload_dir):
            comp_pay = self.compose_payload(payload_dir)
            return {"path": comp_pay}
        else:
            raise TefloReportError("Payload path Not found.")

    def get_json_config_file(self, jconfig_dir):
        """Get provided datarouter json config.
        """
        if os.path.isfile(os.path.join(jconfig_dir,
                                       self.provider_params.get('dr_metadata'))):
            json_config_file = os.path.join(jconfig_dir,
                                            self.provider_params.get('dr_metadata'))
            return json_config_file
        else:
            raise TefloReportError("json_config_file path Not found.")

    def validate(self):
        schema_validator(schema_data=self.build_profile(self.report), schema_files=[self.__schema_file_path__],
                         schema_ext_files=[self.__schema_ext_path__])

    def compose_payload(self, payload_dir):
        self.logger.debug('Starting composing process.')
        try:
            tar_dir_list = compose_pload(payload_dir, self.config['ARTIFACT_FOLDER'], self.workspace)
            tarmembers = validate_compose_payload_content(tar_dir_list)
            self.logger.debug(f'Successfully validate and composed payload dir to {payload_dir}.tar.gz')
            new_p_path = payload_dir + ".tar.gz"
            return new_p_path
        except TefloReportError as ex:
            raise TefloReportError(f'Failed composing payload Dir with error: {ex}.')

    def get_token_regex(self, j_res):
        """Use regex expression to get track id"""

        track_id_reg = re.compile(r'\w{8}-\w{4}-\w{4}-\w{4}-\w{12}')
        trackid_s = track_id_reg.search(j_res['msg'])
        trackid = trackid_s.group()
        return trackid
