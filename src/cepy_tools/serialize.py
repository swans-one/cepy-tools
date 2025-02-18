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
