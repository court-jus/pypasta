"""
Attribute field.

Should be used when a specific attribute can be hooked to a widget.
Field handles the "model to view" part through callbacks.
"""


class Field:
    """
    Definition of a field.
    """

    def __init__(self, default=0, min_value=0, max_value=127):
        self.value = default
        self.min_value = min_value
        self.max_value = max_value
        self.callbacks = {}

    def hook(self, callback, hookname):
        """
        Add this callback to be called when this field's value changes.
        """
        self.callbacks[hookname] = callback
        callback(self.value)

    def unhook(self, hookname):
        """
        Remove a hook.
        """
        if hookname not in self.callbacks:
            return
        self.callbacks.pop(hookname)

    def set_value(self, value):
        """
        Set this field's value and call the hooks.
        """
        if self.min_value is not None:
            value = max(self.min_value, value)
        if self.max_value is not None:
            value = min(self.max_value, value)
        self.value = value
        for callback in self.callbacks.values():
            callback(self.value)

    def increment(self, increment=1):
        """
        Increment/decrement this field's value.
        """
        new_value = self.value + increment
        if self.max_value is not None and new_value > self.max_value:
            if self.min_value is not None:
                new_value = self.min_value + (new_value - self.max_value - 1)
            else:
                new_value = self.max_value
        if self.min_value is not None and new_value < self.min_value:
            if self.max_value is not None:
                new_value = self.max_value + new_value + 1
            else:
                new_value = self.min_value
        self.set_value(new_value)

    def str_value(self):
        """
        Get the str representation of this field's value.
        """
        return str(self.value)

    def get_value(self):
        """
        Get this field value.
        """
        return self.value


class BooleanField(Field):
    """
    This field can hold True/False values.
    """

    def __init__(self, *a, default=False, **kw):
        super().__init__(*a, default=default, **kw)

    def increment(self, _increment=1):
        """
        Alternate between True and False.
        """
        self.set_value(not self.value)


class EnumField(Field):
    """
    This field holds a value limited to a number of choices.
    """

    def __init__(self, *a, default=0, choices=None, **kw):
        super().__init__(*a, default=default, **kw)
        self.choices = choices if choices is not None else []

    def set_value(self, value):
        """
        Set this field's value.
        """
        if value < 0 or value >= len(self.choices):
            return
        self.value = value
        for callback in list(self.callbacks.values()):
            callback(self.value)

    def increment(self, increment=1):
        """
        Increment/decrement this field's value within set choices.
        """
        self.set_value((self.value + increment) % len(self.choices))

    def get_value(self):
        """
        Get the value of the field from the choices.
        """
        return self.choices[self.value]

    def str_value(self):
        """
        Get the str representation of the field's value.
        """
        return str(self.get_value())


class ListField(Field):
    """
    A field that holds a list of values.
    """

    def __init__(self, *a, default=None, **kw):
        super().__init__(
            *a,
            default=default if default is not None else [],
            min_value=None,
            max_value=None,
            **kw
        )

    def get_value(self, index=None):
        """
        Get value.

        If index is specified, return the value in the list at this index.
        """
        if index is not None:
            return self.value[index]
        return self.value

    def increment(self, _increment=1):
        """
        Cannot increment this field's value.
        """

    def str_value(self):
        """
        Get a str representation of this field's value.
        """
        return ", ".join([str(v) for v in self.value])
