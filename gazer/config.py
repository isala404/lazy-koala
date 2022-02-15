import threading
import pyinotify
import yaml
import os

NODE_NAME = os.getenv("NODE_NAME")


class ConfigWatcher(pyinotify.ProcessEvent):
    config = None

    def __init__(self, **kargs):
        super().__init__(**kargs)
        self.read_config()

    def read_config(self):
        with open(r'config/config.yaml') as file:
            self.config = yaml.load(file, Loader=yaml.FullLoader)
            self.config = dict(filter(lambda elem: elem[1]['isService'] or elem[1]['node'] == NODE_NAME,
                                      self.config.items()))

    def process_IN_CLOSE_WRITE(self, evt):
        self.read_config()


config_watcher = ConfigWatcher()
wm = pyinotify.WatchManager()
notifier = pyinotify.Notifier(wm, config_watcher)
wdd = wm.add_watch("config/config.yaml", pyinotify.IN_CLOSE_WRITE)
config_watcher_thread = threading.Thread(target=notifier.loop, args=())
config_watcher_thread.daemon = True
config_watcher_thread.start()
