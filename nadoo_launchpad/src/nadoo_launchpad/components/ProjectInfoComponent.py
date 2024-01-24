import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from toga.sources import ListSource
from nadoo_launchpad.services import add_new_project, cancel_action

class ProjectInfoComponent(toga.Box):
    def __init__(self, app:toga.App, project_data=None):
        super().__init__(style=Pack(direction=COLUMN, padding=5))
        self.app = app
        
        # Set default values if project_data is None
        if project_data is None:
            project_data = {
                "project_name": "Default Project Name",
                "bundle_identifier": "com.example",
                "author_name": "Default Author",
                "author_email": "email@example.com",
                "project_url": "https://example.com",
                "project_description": "Default Description",
                # Set other default values...
            }

        # Mapping of developer names to their emails
        developers = ListSource(
            accessors=["name", "email"],
            data=[
                {
                    "name": "Christoph Backhaus",
                    "email": "christoph.backhaus@nadooit.de",
                },
                {
                    "name": "Laurin Kochwasser",
                    "email": "laurin.kochwasser@nadooit.de"
                },
            ],
        )

        # Dropdown for selecting the developer
        developer_options = developers

        developer_options.append(
            {"name": "Add New...", "email": "NoName.NoName@nadooit.de"}
        )

        self.developer_dropdown_list = toga.Selection(
            items=developer_options, accessor="name", style=Pack(padding=(5, 0))
        )

        # Text input fields
        self.project_name_input = toga.TextInput(
            placeholder="Project Name",
            value="NADOO Launchpad",            
        )

        self.bundle_input = toga.TextInput(
            placeholder="Bundle Identifier",
            value="de.nadooit",
        )

        self.author_input = toga.TextInput(
            placeholder="Author",
            value=self.developer_dropdown_list.value.__dict__.get("name"),
        )
        self.author_email_input = toga.TextInput(
            placeholder="Author's Email",
            value=self.developer_dropdown_list.value.__dict__.get("email"),
        )
        self.url_input = toga.TextInput(placeholder="URL", value="https://nadooit.de/")
        self.description_input = toga.TextInput(
            placeholder="Description", value="A description of the project"
        )

        #Actions
        self.developer_dropdown_list.on_select = self.on_developer_selected
        self.project_name_input.on_change = self.update_project_url
        self.bundle_input.on_change = self.update_project_url


        # Adding widgets to the component
        self.add(self.developer_dropdown_list)
        self.add(self.project_name_input)
        self.add(self.bundle_input)
        self.add(self.author_input)
        self.add(self.author_email_input)
        self.add(self.url_input)
        self.add(self.description_input)

        # Selections
        # Dropdown for selecting the license
        licenses = [
            "BSD license",
            "MIT license",
            "Apache Software License",
            "GNU General Public License v2 (GPLv2)",
            "GNU General Public License v2 or later (GPLv2+)",
            "GNU General Public License v3 (GPLv3)",
            "GNU General Public License v3 or later (GPLv3+)",
            "Proprietary",
            "Other",
        ]
        self.license_dropdown = toga.Selection(
            items=licenses, style=Pack(padding=(5, 0))
        )
        self.license_dropdown.value = "Proprietary"  # Set default value

        # Adding license dropdown to the component
        self.add(self.license_dropdown)

        # Dropdown for selecting the GUI framework
        gui_frameworks = [
            "Toga",
            "PySide2 (does not support iOS/Android deployment)",
            "PySide6 (does not support iOS/Android deployment)",
            "PursuedPyBear (does not support iOS/Android deployment)",
            "Pygame (does not support iOS/Android deployment)",
            "None",
        ]
        self.gui_framework_dropdown = toga.Selection(
            items=gui_frameworks, style=Pack(padding=(5, 0))
        )
        self.gui_framework_dropdown.value = "Toga"  # Set default value

        # Adding GUI framework dropdown to the component
        self.add(self.gui_framework_dropdown)

        # Buttons
        cancel_btn = toga.Button("Cancel", on_press=cancel_action)
        add_project_btn = toga.Button("Add Project", on_press=add_new_project)
        button_box = toga.Box(
            children=[cancel_btn, add_project_btn], style=Pack(direction=ROW, padding=5)
        )
        self.add(button_box)
    def update_project_url(self, widget):
        # Split the bundle input by '.', reverse it, and join back with '.'
        bundle_reversed = ".".join(self.bundle_input.value.split(".")[::-1])
        # Replace spaces with underscores in the project name
        project_name_underscored = self.project_name_input.value.replace(" ", "_")
        # Combine the reversed bundle and the underscored project name
        self.url_input.value = f"http://{bundle_reversed}/{project_name_underscored}"
    
    def on_developer_selected(self, widget):
        selected_developer = self.developer_dropdown_list.value
        if selected_developer:
            selected_developer_name = selected_developer.name
            selected_developer_email = selected_developer.email

        if selected_developer_name == "Add New...":
        # Add a new text input field for the developer's name
            self.author_input.on_change = self.on_new_developer_name_entered
        else:
        # Predefined developer selected
            self.author_input.value = selected_developer_name
            self.author_email_input.value = selected_developer_email