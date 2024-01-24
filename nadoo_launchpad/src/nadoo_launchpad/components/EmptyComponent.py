import toga
from toga.style import Pack
from toga.style.pack import COLUMN

class EmptyComponent(toga.Box):
    def __init__(self, app):
        super().__init__(style=Pack(direction=COLUMN, padding=5))
        self.app = app

        # When the component is opend I want to save the state. That way if the user changed something and then aborted the process I can reset the values to their initial state.
