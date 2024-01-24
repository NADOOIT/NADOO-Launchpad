import toga
from toga.style import Pack
from toga.style.pack import COLUMN
from nadoo_launchpad.services import install

# TODO add setting the secret key on first startup. This can be a random string. Simply use UUID4 to create it
class InstallationComponent(toga.Box):
    def __init__(self, app, ui_blocks:list):
        super().__init__(style=Pack(direction=COLUMN, padding=5))
        self.app = app
        self.install_btn = toga.Button("Install", on_press=install(self=self, ui_blocks=ui_blocks))
        self.add(self.install_btn)

    