import math
from pathlib import Path
import platform
import select
from typing import Self
import venv
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
import subprocess
import os
import sys
import toml
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from toga.widgets.button import OnPressHandler
from toga.sources import ListSource


def get_project_folder_path():
    home_dir = os.path.expanduser("~")
    project_folder = os.path.join(home_dir, "Documents", "GitHub")

    # Create the folder if it doesn't exist
    if not os.path.exists(project_folder):
        os.makedirs(project_folder)

    return project_folder


def get_resource_path():
    pass


class cancel_pres(OnPressHandler):
    pass


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


# TODO add setting the secret key on first startup. This can be a random string. Simply use UUID4 to create it
class InstallationComponent(toga.Box):
    def __init__(self, app):
        super().__init__(style=Pack(direction=COLUMN, padding=5))
        self.app = app
        self.install_btn = toga.Button("Install", on_press=self.install)
        self.add(self.install_btn)

    def update_ui(self):
        # Refresh the UI to show changes
        self.main_window.content = self.new_project_form

    def set_installation_state(self):
        config_path = self.paths.config / "install_state.toml"

        # Ensure the directory exists
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Check if the file exists
        if not config_path.exists():
            # If not, create it with the initial 'installed' state
            config_data = {"installed": True}
        else:
            # If it exists, load the existing data
            with open(config_path, "r") as config_file:
                config_data = toml.load(config_file)

        # Update the 'installed' state to True
        config_data["installed"] = True

        # Save the updated data
        with open(config_path, "w") as config_file:
            toml.dump(config_data, config_file)

    def install(self, widget):
        # Installation logic
        # Update installation state in config file
        self.set_installation_state()

        self.project_folder = self.setup_project_folder()
        self.install_pyenv()
        self.install_python_with_pyenv()
        self.set_installation_state()

        # Correctly initialize ProjectInfoComponent
        self.project_info_component = ProjectInfoComponent(self)
        self.ui_blocks.append(self.project_info_component)

        self.update_ui_post_install()

    def update_ui_post_install(self):
        # Remove the 'Install' button and add the 'New Project' button
        self.main_box.remove(self.install_btn)

    def install_python_with_pyenv(self):
        # Check if the Python version already exists
        pyenv_version_exists = (
            subprocess.run(
                ["pyenv", "versions", "--bare", "--skip-aliases", "3.11.7"],
                capture_output=True,
            ).returncode
            == 0
        )

        # If the version exists, skip installation
        if not pyenv_version_exists:
            # Use 'yes' to automatically answer 'y' to any prompts
            subprocess.run("yes | pyenv install 3.11.7", shell=True)
        else:
            print("Python 3.11.7 is already installed.")

        # Set global version
        subprocess.run(["pyenv", "global", "3.11.7"])

    def install_pyenv(self):
        # Example command, adjust based on OS
        subprocess.run(["curl", "-L", "https://pyenv.run", "|", "bash"])
        # Additional commands may be needed to integrate pyenv into the shell

    def setup_project_folder(self):
        # Get the current user's home directory and set the project folder path
        project_folder = get_project_folder_path()
        return project_folder


class ProjectInfoComponent(toga.Box):
    def __init__(self, app, project_data=None):
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
                {"name": "Laurin Kochwasser", "email": "laurin.kochwasser@nadooit.de"},
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
        self.developer_dropdown_list.on_select = self.on_developer_selected

        # Text input fields
        self.project_name_input = toga.TextInput(
            placeholder="Project Name",
            value="NADOO Launchpad",
            on_change=self.update_project_url,
        )

        self.bundle_input = toga.TextInput(
            placeholder="Bundle Identifier",
            value="de.nadooit",
            on_change=self.update_project_url,
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
        cancel_btn = toga.Button("Cancel", on_press=self.app.cancel_action)
        add_project_btn = toga.Button("Add Project", on_press=self.add_new_project)
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

    def create_and_activate_venv(self):
        os_type = platform.system()
        if os_type == "Darwin":  # macOS
            return self.create_and_activate_venv_mac()
        # Add more conditions for other OS types here
        else:
            print(f"OS {os_type} not supported yet")

    def create_and_activate_venv_mac(self):
        python_path = (
            subprocess.check_output(["pyenv", "which", "python"]).decode().strip()
        )
        # Create the virtual environment inside the project folder
        venv_path = os.path.join(get_project_folder_path(), "env")
        subprocess.run([python_path, "-m", "venv", venv_path])
        # Activate the virtual environment - for macOS
        activate_command = f"source {venv_path}/bin/activate"
        subprocess.run(["bash", "-c", activate_command])

        return venv_path

    def add_new_project(self, widget):
        # Step 1: Create a project folder
        project_name = self.project_name_input.value.replace(" ", "-")
        project_folder = os.path.join(get_project_folder_path(), project_name)
        os.makedirs(project_folder, exist_ok=True)

        # Step 2: Create and activate a virtual environment
        developer_name = self.author_input.value.replace(" ", "_")

        venv_path = self.create_and_activate_venv()

        # Step 3: Install Briefcase in the virtual environment
        pip_path = os.path.join(venv_path, "bin", "pip")
        subprocess.run([pip_path, "install", "briefcase"])

        # Step 4: Create a project template from the entered data
        # (Assuming create_pyproject_file is a method to generate the pyproject.toml file)

        user_data = {
            "project_name": self.project_name_input.value,
            "app_name": self.project_name_input.value.lower().replace(
                " ", "_"
            ),  # Assuming app_name is a lowercase, underscored version of project_name
            "formal_name": self.project_name_input.value,  # Assuming formal_name is the same as project_name
            "bundle_identifier": self.bundle_input.value,
            "author_name": self.author_input.value,
            "author_email": self.author_email_input.value,
            "url": self.url_input.value,
            "description": self.description_input.value,
            "long_description": self.description_input.value,  # Assuming long_description is the same as description
            "license": self.license_dropdown.value,
            "gui_framework": self.gui_framework_dropdown.value,
            "version": "0.0.1",  # Assuming version is a static value
        }

        project_template = self.create_pyproject_file(user_data, project_folder)

        # Step 5: Use Briefcase to create a new project
        briefcase_path = os.path.join(venv_path, "bin", "briefcase")
        briefcase_command = [briefcase_path, "new", "--template", project_folder]
        subprocess.run(briefcase_command, cwd=project_folder)

    def on_new_developer_name_entered(self, widget):
        # Generate the email based on the entered name
        new_name = widget.value
        if new_name:
            new_email = f"{new_name.replace(' ', '.').lower()}@nadooit.de"
            self.author_email_input.value = new_email

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

    def create_pyproject_file(self, user_data, project_folder):
        # Construct the path to the template file
        template_file_name = "base_project_template.toml"
        template_path = Path(self.app.paths.app / "resources" / template_file_name)

        # Ensure the project subfolder exists
        project_subfolder = Path(project_folder, user_data["app_name"])
        project_subfolder.mkdir(parents=True, exist_ok=True)

        # New project file path
        new_project_path = project_subfolder / "pyproject.toml"

        try:
            with open(template_path, "r") as template_file:
                template_content = template_file.read()

            # Replace placeholders with actual data
            for key, value in user_data.items():
                placeholder = "{{" + key.upper() + "}}"
                template_content = template_content.replace(placeholder, value)

            print(template_content)

            # Write the new pyproject.toml file
            with open(new_project_path, "w") as new_project_file:
                new_project_file.write(template_content)

            return new_project_file

        except FileNotFoundError as e:
            self.display_error(f"Template file not found: {e}")
        except IOError as e:
            self.display_error(f"Error while handling the file: {e}")
        except Exception as e:
            self.display_error(f"An unexpected error occurred: {e}")


class EmptyComponent(toga.Box):
    def __init__(self, app):
        super().__init__(style=Pack(direction=COLUMN, padding=5))
        self.app = app

        # When the component is opend I want to save the state. That way if the user changed something and then aborted the process I can reset the values to their initial state.


class NADOOLaunchpad(toga.App):
    def check_installation_state(self):
        # Check the config file for the installation state
        config_path = self.paths.config / "install_state.toml"
        if config_path.exists():
            with open(config_path, "r") as config_file:
                config_data = toml.load(config_file)
            return config_data.get("installed", False)
        return False

    def startup(self):
        self.main_box = toga.Box(style=Pack(direction=COLUMN))

        # Initialize a list to keep track of UI blocks
        self.ui_blocks = []
        ui_blocks_for_this_element = []
        self.initial_values = {}

        # Check if installation has already occurred
        if self.check_installation_state():
            # Add ProjectInfoComponent to UI blocks if already installed
            project_info_component = ProjectInfoComponent(self, project_data=None)
            ui_blocks_for_this_element.append(project_info_component)
        else:
            # Add InstallationComponent to UI blocks if not installed
            installation_component = InstallationComponent(self)
            ui_blocks_for_this_element.append(installation_component)

        self.ui_blocks.append(ui_blocks_for_this_element)

        # Set the initial content of the main window
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.update_main_content()
        self.main_window.show()

    def cancel_action(self, widget):
        # Restore initial values
        if self.ui_blocks:
            self.ui_blocks.pop()
            self.update_main_content()

    def update_main_content(self):
        # Rebuild the main content area based on the UI blocks list
        self.main_window.content = toga.Box(style=Pack(direction=COLUMN))
        for block in self.ui_blocks:
            for element in block:
                self.main_window.content.add(element)

    def display_error(self, error_message):
        # Switch to the error component with the provided message
        error_component = ErrorComponent(self.app, error_message)
        self.app.main_window.content = error_component


def main():
    return NADOOLaunchpad()
