"""
Attribute field.

Should be used when a specific attribute can be hooked to a widget.
Field handles the "model to view" part through callbacks.
"""
import json


SMOOTH_SMALL_LEAP = 0.05
SMOOTH_BIG_LEAP = 0.1


class Field:
    """
    Definition of a field.
    """

    def __init__(
        self, default=0, min_value=0, max_value=127, smooth=False, debug=False
    ):
        self.value = default
        self.modulation = 0
        self.min_value = min_value
        self.max_value = max_value
        self.smooth = smooth
        self.debug = debug
        self.callbacks = {}

    def hook(self, callback, hookname, send_modulation=False):
        """
        Add this callback to be called when this field's value changes.
        """
        self.callbacks[hookname] = (callback, send_modulation)
        if send_modulation:
            callback(self.get_value(), self.modulation)
        else:
            callback(self.get_value())

    def unhook(self, hookname):
        """
        Remove a hook.
        """
        if hookname not in self.callbacks:
            return
        self.callbacks.pop(hookname)

    def set_value(self, value, force=False):
        """
        Set this field's value and call the hooks.
        """
        if self.debug:
            print("set value", value)
        if force or not self.smooth:
            self.value = value
        else:
            self.smoothly_set_value(value)
        if self.min_value is not None:
            self.value = max(self.min_value, self.value)
        if self.max_value is not None:
            self.value = min(self.max_value, self.value)
        for callback, send_modulation in self.callbacks.values():
            if send_modulation:
                callback(self.get_value(), self.modulation)
            else:
                callback(self.get_value())

    def smoothly_set_value(self, new_value):
        """
        Approches new_value but without making too big leaps.
        """
        # Use defaults if min/max are note set
        applied_min = self.min_value if self.min_value is not None else 0
        applied_max = self.max_value if self.max_value is not None else 127
        small_leap = int((applied_max - applied_min) * SMOOTH_SMALL_LEAP)
        leap_to_do = abs(new_value - self.value)
        if leap_to_do <= small_leap:
            self.value = new_value
            return
        leap_to_do = int(leap_to_do * SMOOTH_BIG_LEAP)
        if self.value > new_value:
            self.value -= leap_to_do
        else:
            self.value += leap_to_do

    def increment(self, increment=1):
        """
        Increment/decrement this field's value.
        """
        new_value = self.value + increment
        if self.max_value is not None and new_value > self.max_value:
            new_value = self.max_value
        if self.min_value is not None and new_value < self.min_value:
            new_value = self.min_value
        self.set_value(new_value)

    def str_value(self):
        """
        Get the str representation of this field's value.
        """
        return str(self.get_value())

    def get_value(self):
        """
        Get this field value.
        """
        modulated_value = self.value + self.modulation
        if self.min_value is not None:
            modulated_value = max(self.min_value, modulated_value)
        if self.max_value is not None:
            modulated_value = min(self.max_value, modulated_value)
        if self.debug:
            print(modulated_value)
        return modulated_value

    def get_unmodulated_value(self):
        """
        Return raw value, without modulation.
        """
        return self.value

    def set_modulation(self, value):
        """
        Set modulation for this field (LFO for example).
        """
        self.modulation = value
        for callback, send_modulation in self.callbacks.values():
            if send_modulation:
                callback(self.get_value(), self.modulation)
            else:
                callback(self.get_value())


class StrField(Field):
    """
    A Field holding any str.
    """

    def __init__(self, *a, default="", **kw):
        kw["min_value"] = None
        kw["max_value"] = None
        super().__init__(*a, default=default, **kw)

    def increment(self, _increment=1):
        """
        Cannont increment this.
        """
        return

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

    def get_value(self):
        """
        Get this field value.
        """
        return self.value


class EnumField(Field):
    """
    This field holds a value limited to a number of choices.
    """

    def __init__(self, *a, default=0, choices=None, **kw):
        super().__init__(*a, default=default, **kw)
        self.choices = choices if choices is not None else []

    def set_value(self, value, force=False):
        """
        Set this field's value.
        """
        if value < 0 or value >= len(self.choices):
            return
        self.value = value
        if self.debug:
            print(self.callbacks)
        for callback, send_modulation in list(self.callbacks.values()):
            if send_modulation:
                callback(self.value, self.modulation)
            else:
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

    def increment(self, increment=1, index=None, min_value=None, max_value=None):
        """
        Increment the value at index.
        """
        if index is None:
            return
        new_value = self.value[:]
        if len(new_value) <= index:
            missing_slots = index - (len(new_value) - 1)
            new_value.extend([0] * missing_slots)
        if isinstance(new_value[index], (int, float)):
            new_value[index] += increment
            if min_value is not None and new_value[index] < min_value:
                new_value[index] = min_value
            if max_value is not None and new_value[index] > max_value:
                new_value[index] = max_value
            self.set_value(new_value)

    def set_index_value(self, value, index=None, min_value=None, max_value=None):
        """
        Set the value at index
        """
        if index is None:
            return
        new_value = self.value[:]
        if len(new_value) <= index:
            missing_slots = index - (len(new_value) - 1)
            new_value.extend([0] * missing_slots)
        new_value[index] = value
        if min_value is not None and new_value[index] < min_value:
            new_value[index] = min_value
        if max_value is not None and new_value[index] > max_value:
            new_value[index] = max_value
        self.set_value(new_value)

    def str_value(self):
        """
        Get a str representation of this field's value.
        """
        return ", ".join([str(v) for v in self.value])



class DictField(Field):
    """
    A field that holds a dictionary.
    """

    def __init__(self, *a, default=None, **kw):
        super().__init__(
            *a,
            default=default if default is not None else {},
            min_value=None,
            max_value=None,
            **kw
        )

    def get_value(self, key=None):
        """
        Get value.

        If key is specified, return the value associated with this key.
        """
        if key is not None:
            return self.value.get(key)
        return self.value

    def increment(self, increment=1, key=None, min_value=None, max_value=None):
        """
        Increment the value at key.
        """
        if key is None:
            return
        new_value = self.value[:]
        if key not in new_value:
            new_value[key] = 1
        if isinstance(new_value[key], (int, float)):
            new_value[key] += increment
            if min_value is not None and new_value[key] < min_value:
                new_value[key] = min_value
            if max_value is not None and new_value[key] > max_value:
                new_value[key] = max_value
            self.set_value(new_value)

    def set_key_value(self, value, key=None, min_value=None, max_value=None):
        """
        Set the value at index
        """
        new_value = self.value[:]
        new_value[key] = value
        if min_value is not None and new_value[key] < min_value:
            new_value[key] = min_value
        if max_value is not None and new_value[key] > max_value:
            new_value[key] = max_value
        self.set_value(new_value)

    def str_value(self):
        """
        Get a str representation of this field's value.
        """
        return json.dumps(self.value)
