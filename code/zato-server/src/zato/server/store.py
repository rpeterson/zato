# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import weakref
from copy import deepcopy
from logging import getLogger
from traceback import format_exc

# Bunch
from bunch import Bunch

# Zato
from zato.common import Inactive, PASSWORD_SHADOW

logger = getLogger(__name__)

class BaseAPI(object):
    """ A base class for connection/query APIs.
    """
    def __init__(self, conn_store):
        self._conn_store = conn_store

    def __getitem__(self, name):
        item = self._conn_store.get(name)
        if not item:
            msg = 'No such item `{}` in `{}`'.format(name, sorted(self._conn_store.sessions))
            logger.warn(msg)
            raise KeyError(msg)

        if not item.config.is_active:
            msg = '`{}` is inactive'.format(name)
            logger.warn(msg)
            raise Inactive(msg)

        return item


    def create(self, name, msg, **extra):
        return self._conn_store.create(name, msg, **extra)

    def edit(self, name, msg, **extra):
        return self._conn_store.edit(name, msg, **extra)

    def delete(self, name):
        return self._conn_store.delete(name)

    def change_password(self, config):
        return self._conn_store.change_password(config)

# ################################################################################################################################

class BaseStore(object):
    """ A base class for connection/query stores.
    """
    def __init__(self):
        self.items = {}

        # gevent
        from gevent.lock import RLock

        self.lock = RLock()

    def __getitem__(self, name):
        return self.items[name]

    def get(self, name):
        return self.items.get(name)

    def _create(self, name, config, **extra):
        """ Actually adds a new definition, must be called with self.lock held.
        """
        config_no_sensitive = deepcopy(config)
        config_no_sensitive['password'] = PASSWORD_SHADOW
        item = Bunch(config=config, config_no_sensitive=config_no_sensitive, is_created=False, impl=None)

        try:
            logger.debug('Creating `%s`', config_no_sensitive)
            impl = self.create_impl(config, config_no_sensitive, **extra)

            def execute(session, statement):
                def execute_impl(**kwargs):
                    if not session:
                        raise Exception('Cannot execute the query without a session')
                    return session.execute(statement, kwargs)
                return execute_impl

            item.execute = execute(extra['def_'].conn, impl)

            logger.debug('Created `%s`', config_no_sensitive)
        except Exception, e:
            logger.warn('Could not create `%s`, config:`%s`, e:`%s`', name, config_no_sensitive, format_exc(e))
        else:
            item.extra = weakref.proxy(extra.get('def_'))
            item.impl = impl
            item.is_created = True

        self.items[name] = item

        return item

    def create(self, name, config, **extra):
        """ Adds a new connection definition.
        """
        with self.lock:
            return self._create(name, config, **extra)

    def _delete(self, name):
        """ Actually deletes a definition. Must be called with self.lock held.
        """
        try:
            if not name in self.items:
                raise Exception('No such name `{}` among `{}`'.format(name, self.items.keys()))
            self.delete_impl()
        except Exception, e:
            logger.warn('Error while deleting `%s`, e:`%s`', name, format_exc(e))
        finally:
            del self.items[name]

    def delete(self, name):
        """ Deletes an existing connection.
        """
        with self.lock:
            self._delete(name)

    def _edit(self, name, config, **extra):
        self._delete(name)
        return self._create(config.name, config, **extra)

    def edit(self, name, config, **extra):
        with self.lock:
            self._edit(name, config, **extra)

    def change_password(self, password_data):
        with self.lock:
            new_config = deepcopy(self.items[password_data.name].config_no_sensitive)
            new_config.password = password_data.password
            self.edit(password_data.name, new_config)

    def create_impl(self):
        raise NotImplementedError('Should be overridden by subclasses')

    def delete_impl(self):
        pass # It's OK - sometimes deleting a connection doesn't have to mean doing anything unusual
