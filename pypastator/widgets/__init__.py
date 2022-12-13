class BaseWidget:
    def handle_click(self, pos, callback):
        print("handle click not implemented for", self, "at", pos, "cb", callback)
