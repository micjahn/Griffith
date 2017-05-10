# -*- coding: UTF-8 -*-
# vim: fdm=marker
__revision__ = '$Id$'

# Copyright © 2011
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA

# You may use and distribute this software under the terms of the
# GNU General Public License, version 2 or later

import logging

from sqlalchemy.orm.interfaces import AttributeExtension
try:
    # sql alchemy 0.8 (and above)
    from sqlalchemy.ext.instrumentation import InstrumentationManager
except:
    # sql alchemy 0.7
    from sqlalchemy.orm.interfaces import InstrumentationManager
from sqlalchemy.orm import ColumnProperty
from sqlalchemy.types import String

use_pre_07 = False
try:
    from sqlalchemy import event
except:
    use_pre_07 = True

log = logging.getLogger('Griffith')

class InstallValidatorListeners(InstrumentationManager):
    def post_configure_attribute(self, class_, key, inst):
        if use_pre_07:
            self.post_configure_attribute_pre_07(class_, key, inst)
        else:
            self.post_configure_attribute_07(class_, key, inst)
        
    def post_configure_attribute_07(self, class_, key, inst):
        """Add validators for any attributes that can be validated."""
        # SQLAlchemy >= 0.7 (using events)
        prop = inst.prop
        # Only interested in simple columns, not relations
        if isinstance(prop, ColumnProperty) and len(prop.columns) == 1:
            col = prop.columns[0]
            # if we have string column with a length, install a length validator
            if isinstance(col.type, String) and col.type.length:
                event.listen(inst, 'set', LengthValidator(col.name, col.type.length).set, retval=True)

    def post_configure_attribute_pre_07(self, class_, key, inst):
        """Add validators for any attributes that can be validated."""
        # SQLAlchemy < 0.7 (using extensions)
        prop = inst.prop
        # Only interested in simple columns, not relations
        if isinstance(prop, ColumnProperty) and len(prop.columns) == 1:
            col = prop.columns[0]
            # if we have string column with a length, install a length validator
            if isinstance(col.type, String) and col.type.length:
                inst.impl.extensions.insert(0, LengthValidator(col.name, col.type.length))


class ValidationError(Exception):
    pass


class LengthValidator(AttributeExtension):
    def __init__(self, name, max_length):
        self.name = name
        self.max_length = max_length

    def set(self, state, value, oldvalue, initiator):
        if value and len(value) > self.max_length:
            # can be changed so that an exception is raised which can be shown in UI
            # but at the moment an exception is silently lost, only written to console
            #raise ValidationError("Length %d exceeds allowed %d for %s" %
            #                    (len(value), self.max_length, self.name))
            log.warning("Length %d exceeds allowed %d for %s; truncating value" %
                                (len(value), self.max_length, self.name))
            return value[0:self.max_length]
        return value
