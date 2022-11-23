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
    tests.test_datarouter_plugin.py

    Unit tests for testing datarouter_plugin

    :copyright: (c) 2022 Red Hat, Inc.
    :license: GPLv3, see LICENSE for more details.
"""

from teflo.exceptions import TefloReportError
from teflo_datarouter_plugin.datarouter_plugin import DataRouterPlugin
from teflo.utils.config import Config
from teflo.resources import Report, Execute
from requests.models import Response
import pytest
import mock
import json
import os

from teflo_datarouter_plugin.helpers import get_oauth_token, get_req_status


@pytest.fixture(scope='class')
def config():
    config_file = './../localhost_scenario/teflo.cfg'
    os.environ['TEFLO_SETTINGS'] = config_file
    config = Config()
    config.load()
    return config


@pytest.fixture(scope='class')
def artifact_locations():
    artifacts = dict()
    artifacts['artifacts/host01'] = ['../assets/plugin_demo/']
    return artifacts


@pytest.fixture(scope='class')
def execute(artifact_locations):
    return Execute(
        name='dr_execute',
        parameters=dict(artifact_locations=artifact_locations,
                        executor='runner',
                        hosts='host1')
    )


@pytest.fixture(scope='class')
def execute_no_art():
    return Execute(
        name='dr_execute',
        parameters=dict(executor='runner',
                        hosts='host1')
    )


@pytest.fixture(scope='class')
def default_params(execute):
    params = dict(executes=[execute],
                  provider=dict(name='plugin_demo',
                                credential='datarouter-creds',
                                dr_metadata='user_config.json',
                                )
                  )
    return params


@pytest.fixture(scope='class')
def default_params_no_art(execute_no_art):
    params = dict(provider=dict(name='plugin_demo',
                                credential='datarouter-creds',
                                dr_metadata='user_config.json',
                                )
                  )
    return params


@pytest.fixture(scope='class')
def report(default_params, config):
    return Report(
        name='plugin_demo',
        config=config,
        importer='datarouter',
        parameters=default_params,
    )


@pytest.fixture(scope='class')
def report_no_art(default_params_no_art, config):
    return Report(
        name='plugin_demo',
        config=config,
        importer='datarouter',
        parameters=default_params_no_art,
    )


@pytest.fixture(scope='class')
def datarouter_api_plugin(report):

    dr_api_plugin = DataRouterPlugin(report)
    dr_api_plugin.workspace = '/tmp'
    dr_api_plugin.datafolder = '/tmp'
    return dr_api_plugin


@pytest.fixture(scope='class')
def datarouter_api_plugin_no_art(report_no_art):

    dr_api_plugin = DataRouterPlugin(report_no_art)
    dr_api_plugin.workspace = './../assets'
    dr_api_plugin.datafolder = '/tmp'
    return dr_api_plugin


class TestDRPlugin(object):

    @staticmethod
    def test_validate_dr_payload(datarouter_api_plugin):
        """ This test verifies a given Payload file exists """
        get_payload = datarouter_api_plugin.get_tar_payload_dir('./../assets/plugin_demo')
        assert get_payload['path'] == '/tmp/.results/datarouter/plugin_demo.tar.gz'

    @staticmethod
    def test_validate_dr_payload_no_artifacts(datarouter_api_plugin_no_art):
        """ This test verifies a given Payload file exists Without artifact """
        get_payload = datarouter_api_plugin_no_art.get_tar_payload_dir('./../assets/plugin_demo')
        assert get_payload['path'] == '/tmp/.results/datarouter/plugin_demo.tar.gz'

    @staticmethod
    def test_non_validate_dr_payload(datarouter_api_plugin_no_art):
        """ This test verifies an Error when payload file Not exists """
        with pytest.raises(TefloReportError,  match='Payload path Not found.'):
            datarouter_api_plugin_no_art.get_tar_payload_dir('./../assets/test')

    @staticmethod
    def test_validate_dr_json_path_exist_1(datarouter_api_plugin):
        """ This test verifies a given json file exists """
        os.system('touch /tmp/user_config.json')
        assert datarouter_api_plugin._validate_dr_json_path_exist('user_config.json') == '/tmp/user_config.json'
        os.system('rm /tmp/user_config.json')

    @staticmethod
    def test_validate_dr_json_path_exist_2(datarouter_api_plugin):
        """ This test verifies an error is raised when json file does not exist """
        with pytest.raises(TefloReportError,  match='Data Router Config json file not found'):
            datarouter_api_plugin._validate_dr_json_path_exist('asd.json')

    @staticmethod
    def test_validate_method_with_correct_schema(datarouter_api_plugin):
        """The test is for when validate method works when correctly with correct schema"""
        assert datarouter_api_plugin.validate() == None

    @staticmethod
    @mock.patch('teflo_datarouter_plugin.helpers.requests.post')
    def test_missing_creds_get_token_call(mock_method, datarouter_api_plugin):
        """ This test POST ACCESS TOKEN"""
        op0 = {
                "status_code": 200,
                "content": 'This is A test',
            }
        mock_method.return_value = op0
        datarouter_api_plugin.provider_credentials = dict(dr_client_id='test',
                                                          host_url='https://test.url.com',)
        with pytest.raises(TypeError,  match='dr_client_secret'):
            get_oauth_token(dr_token_url='https://test.url.com/token', dr_client_id='test')

    @staticmethod
    @mock.patch('teflo_datarouter_plugin.datarouter_plugin.requests.put')
    def test_send_put_req(mock_method, datarouter_api_plugin):
        """Test for PAYLOAD PUT req. GET TOKEN FOR TRACKING"""

        op0 = Response()
        op0.status_code = 201
        op0._content = b'{"msg": "This is a test string 00000000-0000-0000-0000-000000000000"}'

        datarouter_api_plugin.provider_credentials = dict(host_url='https://test.url.com')
        mock_method.return_value = op0
        results = datarouter_api_plugin.send_put_req(access_token="testacceesstoke.com",
                                                     tar_payload={"path": "../assets/plugin_test.tar.gz"},
                                                     json_config_file="../assets/user_config.json")
        assert results == '00000000-0000-0000-0000-000000000000'

    @staticmethod
    @mock.patch('teflo_datarouter_plugin.helpers.requests.get')
    def test_track_req_ok(mock_method, datarouter_api_plugin):
        """Test for PAYLOAD PUT req. GET TOKEN FOR TRACKING"""

        op0 = Response()
        op0.status_code = 200
        op0._content = b'{"status": "OK", "request_id": "00000000-0000-0000-0000-000000000000", "targets": {"test1":' \
                       b' {"status": "OK"}, "test2": {"status": "OK"}}}'

        datarouter_api_plugin.provider_credentials = dict(host_url='https://test.url.com')
        mock_method.return_value = op0
        results = get_req_status(dr_client_id='test', dr_client_secret='secret', dr_token_url='https://api.test/token',
                                 get_url='https://api.test/123-123-123', ac_token='token')
        assert results['status'] == 'OK'

    @staticmethod
    @mock.patch('teflo_datarouter_plugin.helpers.requests.get')
    def test_track_req_pending(mock_method, datarouter_api_plugin):
        """Test for PAYLOAD PUT req. GET TOKEN FOR TRACKING"""

        op0 = Response()
        op0.status_code = 200
        op0._content = b'{"status": "PENDING", "request_id": "00000000-0000-0000-0000-000000000000", "targets":' \
                       b' {"test1": {"status": "OK"}, "test2": {"status": "OK"}}}'

        datarouter_api_plugin.provider_credentials = dict(host_url='https://test.url.com')
        mock_method.return_value = op0
        with pytest.raises(TefloReportError,  match='max wait to response is 5min'):
            get_req_status(dr_client_id='test', dr_client_secret='secret', dr_token_url='https://api.test/token',
                           get_url='https://api.test/123-123-123', ac_token='token', req_count=9)

    @staticmethod
    @mock.patch('teflo_datarouter_plugin.helpers.requests.get')
    def test_track_req_failure(mock_method, datarouter_api_plugin):
        """Test for PAYLOAD PUT req. GET TOKEN FOR TRACKING"""

        op0 = Response()
        op0.status_code = 200
        op0._content = b'{"status": "FAILURE", "request_id": "00000000-0000-0000-0000-000000000000", "targets":' \
                       b' {"test1": {"status": "OK"}, "test2": {"status": "OK"}}}'

        datarouter_api_plugin.provider_credentials = dict(host_url='https://test.url.com')
        mock_method.return_value = op0
        with pytest.raises(TefloReportError,  match='req with id 00000000-0000-0000-0000-000000000000 failed'):
            get_req_status(dr_client_id='test', dr_client_secret='secret', dr_token_url='https://api.test/token',
                           get_url='https://api.test/123-123-123', ac_token='token')
