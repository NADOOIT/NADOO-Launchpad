import toga
from toga.style import Pack
from toga.style.pack import COLUMN


class ErrorComponent(toga.Box):
    def __init__(self, app, error_message):
        super().__init__(style=Pack(direction=COLUMN, padding=5))
        self.app = app
        self.error_message = error_message

        # Error message text area
        self.error_text_area = toga.TextInput(readonly=True, value=self.error_message)
        self.add(self.error_text_area)

        # Copy button
        copy_btn = toga.Button("Copy Error", on_press=self.copy_error)
        self.add(copy_btn)

    def copy_error(self, widget):
        # Copy error message to clipboard
        self.app.clipboard.set(self.error_message)
    