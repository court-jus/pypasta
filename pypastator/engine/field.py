class Field:
    def __init__(self, default=0, min_value=0, max_value=127):
        self.value = default
        self.min_value = min_value
        self.max_value = max_value
        self.callbacks = {}

    def hook(self, cb, hookname):
        self.callbacks[hookname] = cb
        cb(self.value)

    def unhook(self, hookname):
        if hookname not in self.callbacks:
            return
        self.callbacks.pop(hookname)

    def set_value(self, value):
        if self.min_value is not None:
            value = max(self.min_value, value)
        if self.max_value is not None:
            value = min(self.max_value, value)
        self.value = value
        for cb in self.callbacks.values():
            cb(self.value)

    def increment(self, increment=1):
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
        return str(self.value)

    def get_value(self):
        return self.value


class BooleanField(Field):
    def __init__(self, default=False, *a, **kw):
        super().__init__(default)

    def set_value(self, value):
        self.value = bool(value)
        for cb in self.callbacks.values():
            cb(self.value)

    def increment(self, increment=1):
        self.set_value(not self.value)


class EnumField(Field):
    def __init__(self, default=0, choices=[], *a, **kw):
        super().__init__(default)
        self.choices = choices

    def set_value(self, value):
        if value < 0 or value >= len(self.choices):
            return
        self.value = value
        for cb in self.callbacks.values():
            cb(self.value)

    def increment(self, increment=1):
        self.set_value((self.value + increment) % len(self.choices))

    def get_value(self):
        return self.choices[self.value]

    def str_value(self):
        return str(self.get_value())


class ListField(Field):
    def __init__(self, default=[], *a, **kw):
        super().__init__(default, *a, **kw)

    def set_value(self, value):
        self.value = value
        for cb in self.callbacks.values():
            cb(self.value)

    def increment(self, increment=1):
        pass

    def str_value(self):
        return ", ".join([str(v) for v in self.value])
