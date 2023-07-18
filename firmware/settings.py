import json

class Settings(object):

    def __init__(self, filename="settings.json"):
        self.filename = filename
        self.settings = {}
        self.load()

    def load(self):
        try:
            with open(self.filename, "r") as f:
                self.settings = json.load(f)
        except OSError:
            self.settings = {}

    def save(self):
        with open(self.filename, "w") as f:
            json.dump(self.settings, f)

    def __getattr__(self, name):
        if name in self.settings:
            return self.settings[name]
        else:
            raise AttributeError

    def set(self, name, value):
        self.settings[name] = value
        self.save()