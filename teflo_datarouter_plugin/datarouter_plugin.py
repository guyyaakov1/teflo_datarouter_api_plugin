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
from teflo.helpers import schema_validator
from teflo.exceptions import TefloReportError, TefloError
from .helpers import compose_pload, send_post_req
import os
import re
import json


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

        if self.provider_credentials['auth_url'] and self.provider_credentials['host_url']\
                and self.provider_credentials['dr_client_secret'] and self.provider_credentials['dr_client_id']:
            dr_url = self.provider_credentials['host_url'] + '/api/results'
            dr_token_url = self.provider_credentials['auth_url']
        else:
            raise TefloReportError("DataRouter Credentials are not set in teflo.cfg")

        payload_dir = self.get_artifacts()

        tar_payload = self.get_tar_payload_dir(payload_dir)
        json_config_file = self.get_json_config_file()

        # Get access Token
        ac_token = self.get_oauth_token(dr_token_url)

        # SEND PUT REQ AND RETURN TRACK ID

        results = {"request_uuid": self.send_put_req(ac_token, dr_url, tar_payload, json_config_file)}
        json_token = json.dumps(results, indent=4)
        json_fname = f"{results['request_uuid']}.json"
        # Create json with token on .results dir.
        dr_results_dir = self.get_dr_results_dir()
        targ_dest = os.path.join(dr_results_dir, json_fname)
        with open(targ_dest, "w") as json_out:
            json_out.write(json_token)

        return results

    def get_artifacts(self):

        # CHECK IF PAYLOAD EXIST IN ARTIFACTS ELSE GO TO .results
        get_report_name = self.report_name.split('/', 1)[0]
        if self.artifacts and os.path.exists(self.artifacts[0]):
            payload_dir = f'{self.artifacts[0].split(get_report_name, 1)[0]}/{get_report_name}'
            if not os.path.exists(payload_dir):
                raise TefloReportError("Payload path Not found.")
        else:
            payload_dir = os.path.join(self.config['RESULTS_FOLDER'],
                                       get_report_name)
        return payload_dir

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
            dr_token_req = send_post_req(dr_token_url=dr_token_url, body=body)
            self.logger.debug('Successfully Generated access token from DR API.')
            return dr_token_req['access_token']
        except Exception as ex:
            raise TefloError(f'Generating access token from DR API Failed with error: {ex}')

    def send_put_req(self, access_token, dr_url, tar_payload, json_config_file):
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
                data = res.json()
                self.logger.info('Data send successfully ro DR API.')
                j_res = data['msg']
                self.logger.info(f'{j_res}')
                get_regex = self.get_result_uuid_regex(j_res)
                return get_regex
            else:
                raise TefloReportError(f'PUT req has Failed with err  {res.content}.')
        except Exception as ex:
            raise TefloReportError(f'Failed Sending PUT req with error: {ex}')

    def get_tar_payload_dir(self, payload_dir):
        """Get provided datarouter payload and check if it needs to be composed into a tar.gz
        """
        try:
            if self.report_name.endswith('.tar.gz') \
                    and os.path.exists(payload_dir):
                self.logger.debug(f"Found valid payload {payload_dir}")
                return {"path": payload_dir}
            elif os.path.isdir(payload_dir):
                comp_pay = self.get_composed_payload_path(payload_dir)
                return {"path": comp_pay}
            else:
                raise TefloReportError("Payload path Not found.")
        except TefloReportError as ex:
            raise TefloReportError(f'Get Payload Failed with err: {ex}')

    def get_json_config_file(self):
        """Get provided datarouter json config.
        """
        validate_path = os.path.join(self.workspace,
                                     self.provider_params.get('dr_metadata'))
        if os.path.isfile(validate_path):
            json_config_file = validate_path
            return json_config_file
        else:
            raise TefloReportError("json_config_file path Not found.")

    def get_dr_results_dir(self):
        # creating a folder under .results dir which will collect all the DR Plugin data created by Teflo.
        dr_payload_dir = os.path.join(self.config['RESULTS_FOLDER'], 'datarouter')
        if not os.path.isdir(dr_payload_dir):
            os.system('mkdir %s' % os.path.abspath(dr_payload_dir))

        return dr_payload_dir

    def get_composed_payload_path(self, payload_dir):
        self.logger.debug('Starting composing process.')
        try:
            get_report_name = self.report_name.split('/', 1)[0]
            targ_dest = os.path.join(self.get_dr_results_dir(), get_report_name)
            compose_path = compose_pload(payload_dir, targ_dest)
            self.logger.debug(f'Successfully composed payload dir to {compose_path}')
            return compose_path
        except TefloReportError as ex:
            raise TefloReportError(f'Failed composing payload Dir with error: {ex}.')

    def get_result_uuid_regex(self, j_res):
        """Use regex expression to get track id"""
        try:
            track_id_reg = re.compile(r'\w{8}-\w{4}-\w{4}-\w{4}-\w{12}')
            trackid_s = track_id_reg.search(j_res)
            trackid = trackid_s.group()
            return trackid
        except Exception as ex:
            raise TefloError(f'Failed getting results ID from str with err: {ex}')

    def validate(self):
        schema_validator(schema_data=self.build_profile(self.report), schema_files=[self.__schema_file_path__],
                         schema_ext_files=[self.__schema_ext_path__])
