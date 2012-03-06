# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at gefira.pl>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing

# lxml
from lxml import etree
from lxml.objectify import Element

# Zato
from zato.common import ZATO_OK
from zato.common.odb.query import basic_auth_list, tech_acc_list, wss_list
from zato.server.service.internal import _get_params, AdminService

class GetList(AdminService):
    """ Returns a list of all security definitions available.
    """
    def handle(self, *args, **kwargs):
        
        with closing(self.server.odb.session()) as session:
            params = _get_params(kwargs.get('payload'), ['cluster_id'], 'data.')
            definition_list = Element('definition_list')

            pairs = (('basic_auth', basic_auth_list), 
                     ('tech_acc', tech_acc_list), 
                     ('wss_username_password', wss_list))
            
            for def_type, meth in pairs:
                
                definitions = meth(session, params['cluster_id'], False)
                for definition in definitions:
        
                    definition_elem = Element('definition')
                    definition_elem.id = definition.id
                    definition_elem.name = definition.name
                    definition_elem.def_type = def_type
        
                    definition_list.append(definition_elem)
    
            return ZATO_OK, etree.tostring(definition_list)