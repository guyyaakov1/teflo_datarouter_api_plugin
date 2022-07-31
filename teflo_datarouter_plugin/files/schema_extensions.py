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
    Pykwalify extensions module.
    Module containing custom validation functions used for schema checking.
    :copyright: (c) 2022 Red Hat, Inc.
    :license: GPLv3, see LICENSE for more details.
"""


def check_creds(value, rule_obj, path):
    """Verify if create_creds is set true in teflo.cfg then all the required credential params are provided"""

    if not (value.get('dr_client_id') and value.get('dr_client_secret')
            and value.get('auth_url') and value.get('host_url')):
        raise AssertionError("Credentials for teflo_dataRouter_api_plugin are not set correctly "
                             "using teflo.cfg")
    else:
        return True


def type_str_list(value, rule_obj, path):
    """Verify a key's value is either a string or list."""
    if not isinstance(value, (str, list)):
        raise AssertionError(
            '%s must be either a string or list.' % path.split('/')[-1]
        )
    return True


# Add any custom schema validation methods here
