from engine.field import Field


class BaseWidget:
    def __init__(self):
        self.hooked_to = {}

    def handle_click(self, pos, callback):
        pass

    def hook(
        self, instance, attrname, hook_name, set_text=False, value_getter=None
    ):
        if hook_name in self.hooked_to:
            self.unhook(hook_name)

        def cb(value):
            if value_getter:
                value = value_getter()
            if set_text and self.text != str(value):
                self.set_text(str(value))
            elif not set_text and self.value != value:
                self.set_value(value)

        field = getattr(instance, attrname)
        if isinstance(field, Field):
            field.hook(cb, hook_name)
            self.hooked_to[hook_name] = [instance, attrname]

    def unhook(self, hook_name = None):
        if hook_name is None:
            for hook_name, [instance, attrname] in self.hooked_to.items():
                field = getattr(instance, attrname)
                if isinstance(field, Field):
                    field.unhook(hook_name)
                    self.hooked_to = {}
        else:
            instance, attrname = self.hooked_to[hook_name]
            field = getattr(instance, attrname)
            if isinstance(field, Field):
                field.unhook(hook_name)
                self.hooked_to = {}

    def highlight(self):
        if hasattr(self, "label") and self.label:
            self.label.set_value(True)

    def shade(self):
        if hasattr(self, "label") and self.label:
            self.label.set_value(False)
