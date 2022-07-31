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
from click.testing import CliRunner
from teflo_datarouter_plugin.helpers import compose_pload, validate_compose_payload_content


@pytest.fixture(scope='class')
def runner():
    return CliRunner()


class TestDRPlugin(object):

    @staticmethod
    def test_payload_compose_sdf():
        """This is for testing use of remote include"""

        getlistdir = compose_pload(payload_dir='../assets/plugin_demo')
        results = validate_compose_payload_content(getlistdir)
        assert 'Validate payload successfully' in results


