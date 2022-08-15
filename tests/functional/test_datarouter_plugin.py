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

import pytest
import mock
import json
import os
from teflo_datarouter_plugin.datarouter_plugin import DataRouterPlugin
from teflo.utils.config import Config
from teflo_datarouter_plugin.helpers import compose_pload, validate_compose_payload_content, send_get_req
from teflo.resources import Report, Execute


@pytest.fixture(scope='class')
def config():
    config_file = '../assets/teflo.cfg'
    os.environ['TEFLO_SETTINGS'] = config_file
    config = Config()
    config.load()
    return config


@pytest.fixture(scope='class')
def artifact_locations():
    artifacts = dict()
    artifacts['artifacts/host01'] = ['../assets/']

    return artifacts


@pytest.fixture(scope='class')
def execute(artifact_locations, config):
    return Execute(
        name='dr_execute',
        parameters=dict(artifact_locations=artifact_locations,
                        executor='runner',
                        hosts='host1')
    )


@pytest.fixture(scope='class')
def default_params(execute):
    params = dict(executes=[execute],
                  provider=dict(name='plugin_demo',
                                credential='datarouter-creds',
                                dr_metadata='../localhost_scenario/user_input.json',
                                )
                  )
    return params


@pytest.fixture(scope='class')
def report(default_params, config):
    return Report(
        name='plugin_demo/',
        config=config,
        importer='datarouter',
        parameters=default_params,
    )


@pytest.fixture(scope='class')
def datarouter_api_plugin(report):

    dr_api_plugin = DataRouterPlugin(report)
    dr_api_plugin.workspace = '../assets/'
    dr_api_plugin.datafolder = '/assets/'
    return dr_api_plugin


class TestDRPlugin(object):

    @staticmethod
    def test_payload_compose_sdf(datarouter_api_plugin):
        """This is for testing payload"""
        datarouter_api_plugin.artifacts = ['../assets/']
        assert datarouter_api_plugin.compose_payload('../assets/plugin_demo')
        # getlistdir = compose_pload(payload_dir='../assets/plugin_demo')
        # results = validate_compose_payload_content(getlistdir)
        # assert 'Validate payload successfully' in results

    # @staticmethod
    # @mock.patch('teflo_datarouter_plugin.helpers.send_get_req')
    # def test_get_token_call(mock_method):
    #     """ This test verifies correct results are created when exec_local_cmd returns rc=0"""
    #     mock_method.return_value = "../assets/get_token.json"
    #     # mock_gettoken_call = mock.Mock(name="mock_gettoken_call",
    #     #                                return_value="../assets/get_token.json")
    #     # mock_gettoken_call.assert_called()
    #     body = {
    #             'grant_type': 'client_credentials',
    #             'client_id': "dr_client_id",
    #             'client_secret': "dr_client_secret",
    #             'scope': 'openid',
    #         }
    #     res = send_get_req(dr_token_url="https://www.tesst.com", body=body)
    #     assert res.res.status_code == 200


# fix Teflo error created by pycodestyle update and update copyright.
# help Omri from  Managed Services Integration Team about create request to create service account. 201


