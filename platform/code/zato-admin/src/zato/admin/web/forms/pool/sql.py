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
import sys
from operator import itemgetter

# Django
from django import forms
from django.forms.util import ErrorList

# Zato
from zato.admin.settings import engine_friendly_name
from zato.admin.web.server_model import SQLConnectionPool

class SQLConnectionPoolForm(forms.Form):
    original_pool_name = forms.CharField(widget=forms.HiddenInput())
    pool_name = forms.CharField(widget=forms.TextInput(attrs={"class":"required"}))
    engine = forms.ChoiceField(widget=forms.Select(attrs={"class":"required"}))
    host = forms.CharField(widget=forms.TextInput(attrs={"class":"required"}))
    db_name = forms.CharField(widget=forms.TextInput(attrs={"class":"required"}))
    user = forms.CharField(widget=forms.TextInput(attrs={"class":"required"}))
    pool_size = forms.IntegerField(widget=forms.TextInput(attrs={"class":"required validate-digits", "style":"width:30px"}))
    extra = forms.CharField(widget=forms.Textarea())
    temp_id = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, prefix=None, post_data=None):
        super(SQLConnectionPoolForm, self).__init__(post_data, prefix=prefix)
        self.fields["engine"].choices = []

        # Sort engines by their friendly name.
        engines = sorted(engine_friendly_name.iteritems(), key=itemgetter(1))

        for engine, friendly_name in engines:
            self.fields["engine"].choices.append([engine, friendly_name])