# cepy-tools - a sleepy little chinese-english python toolkit
#
# Copyright (C) 2025 Erik Swanson
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import functools

def class_serializer(*serialize_auto):
    """A method decorator factor to help seralize the easy attributes.

    Modifies the dectorated seralize function to additionally return
    the attribute from `self.getattr`.

    This should be used for attributes for which no further processing
    will be required for serialization. Any attributes which require
    further processing should be returned from the decorated function.

    # Usage:

    ```
    @class_serializer("easy_propery_1, easy_property_2")
    def serialize(self):
        return { "hard_property": self.hard_property.serialize() }
    ```
    """
    def class_serializer_inner(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            auto_seralized = {k: getattr(self, k) for k in serialize_auto}
            return auto_seralized | func(self, *args, **kwargs)
        return wrapper
    return class_serializer_inner
