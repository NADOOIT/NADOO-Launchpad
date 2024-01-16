import math
import platform
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
import subprocess
import os
import sys
import toml


class NADOOLaunchpad(toga.App):
    def startup(self):
        # Mapping of developer names to their emails
        self.developers = {
            "Christoph Backhaus": "christoph.backhaus@nadooit.de",
            "Laurin Kochwasser": "laurin.kochwasser@nadooit.de",
        }
        self.main_box = toga.Box(style=Pack(direction=COLUMN))

        self.install_btn = toga.Button("Install", on_press=self.install)
        self.main_box.add(self.install_btn)

        # Initialize a list to keep track of UI blocks
        self.ui_blocks = []
        self.initial_values = {}

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = self.main_box
        self.main_window.show()

    def install(self, widget):
        self.project_folder = self.setup_project_folder()
        self.install_pyenv()
        self.install_python_with_pyenv()
        self.set_installation_state()
        self.update_ui_post_install()

    def update_ui_post_install(self):
        # Remove the 'Install' button and add the 'New Project' button
        self.main_box.remove(self.install_btn)
        new_project_btn = toga.Button("New Project", on_press=self.create_new_project)
        self.main_box.add(new_project_btn)

    def cancel_action(self, widget):
        # Restore initial values
        if self.ui_blocks:
            self.restore_initial_values()
            self.ui_blocks.pop()
            self.update_main_content()

    def restore_initial_values(self):
        # Restore the value of each input field to its initial state
        if "project_name" in self.initial_values:
            self.project_name_input.value = self.initial_values["project_name"]

        # Add code to restore other input fields if necessary

    def update_main_content(self):
        # Rebuild the main content area based on the UI blocks list
        self.main_window.content = toga.Box(style=Pack(direction=COLUMN))
        for block in self.ui_blocks:
            self.main_window.content.add(block)

    def create_new_project(self, widget):
        self.new_project_form = toga.Box(style=Pack(direction=COLUMN, padding=5))

        # Dropdown for selecting the developer
        developer_options = list(self.developers.keys()) + ["Add New..."]
        self.developer_dropdown = toga.Selection(
            items=developer_options, style=Pack(padding=(5, 0))
        )
        self.developer_dropdown.on_select = self.on_developer_selected

        # Adding dropdown to the form
        self.new_project_form.add(self.developer_dropdown)

        # Text input fields
        self.project_name_input = toga.TextInput(
            placeholder="Project Name", value="NADOO Launchpad"
        )
        self.bundle_input = toga.TextInput(
            placeholder="Bundle Identifier", value="de.nadooit"
        )
        self.author_input = toga.TextInput(placeholder="Author", value="Your Name")
        self.author_email_input = toga.TextInput(
            placeholder="Author's Email", value="your.email@example.com"
        )
        self.url_input = toga.TextInput(placeholder="URL", value="https://nadooit.de/")
        self.description_input = toga.TextInput(
            placeholder="Description", value="A description of the project"
        )

        # Adding widgets to the form
        self.new_project_form.add(self.developer_dropdown)
        self.new_project_form.add(self.project_name_input)
        self.new_project_form.add(self.bundle_input)
        self.new_project_form.add(self.author_input)
        self.new_project_form.add(self.author_email_input)
        self.new_project_form.add(self.url_input)
        self.new_project_form.add(self.description_input)

        # Selections
        self.license_label = toga.Label(
            "License: Proprietary (click to change)", style=Pack(padding=(5, 0))
        )
        self.gui_framework_label = toga.Label(
            "GUI Framework: Toga (click to change)", style=Pack(padding=(5, 0))
        )
        self.new_project_form.add(self.license_label)
        self.new_project_form.add(self.gui_framework_label)

        self.new_project_form.add(self.extra_options)

        # Buttons
        cancel_btn = toga.Button("Cancel", on_press=self.cancel_action)
        add_project_btn = toga.Button("Add Project", on_press=self.add_new_project)
        button_box = toga.Box(
            children=[cancel_btn, add_project_btn], style=Pack(direction=ROW, padding=5)
        )
        self.new_project_form.add(button_box)

        # Update the main content area
        self.main_window.content = self.new_project_form

    def on_developer_selected(self, widget):
        selected_developer = widget.value
        if selected_developer in self.developers:
            # Predefined developer selected
            self.author_input.value = selected_developer
            self.author_email_input.value = self.developers[selected_developer]
        elif selected_developer == "Add New...":
            # Add a new text input field for the developer's name
            self.new_developer_input = toga.TextInput(placeholder="New Developer Name")
            self.new_developer_input.on_change = self.on_new_developer_name_entered
            self.new_project_form.add(self.new_developer_input)
            self.update_ui()

    def on_new_developer_name_entered(self, widget):
        # Generate the email based on the entered name
        new_name = widget.value
        if new_name:
            new_email = f"{new_name.replace(' ', '.').lower()}@nadooit.de"
            self.author_input.value = new_name
            self.author_email_input.value = new_email

    def update_ui(self):
        # Refresh the UI to show changes
        self.main_window.content = self.new_project_form

    def check_installation_state(self):
        # Adjust the path to the install_state.conf in the resources directory
        resources_path = self.main_window.app.resource_path / "resources"
        config_path = resources_path / "install_state.conf"
        return os.path.exists(config_path)

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

    def setup_project_folder(self):
        # Get the current user's home directory and set the project folder path
        home_dir = os.path.expanduser("~")
        project_folder = os.path.join(home_dir, "Documents", "GitHub")

        # Create the folder if it doesn't exist
        if not os.path.exists(project_folder):
            os.makedirs(project_folder)
        return project_folder

    def create_and_activate_venv(self):
        os_type = platform.system()
        if os_type == "Darwin":  # macOS
            self.create_and_activate_venv_mac()
        # Add more conditions for other OS types here
        else:
            print(f"OS {os_type} not supported yet")

    def create_and_activate_venv_mac(self):
        python_path = (
            subprocess.check_output(["pyenv", "which", "python"]).decode().strip()
        )
        # Create the virtual environment inside the project folder
        venv_path = os.path.join(self.project_folder, "env")
        subprocess.run([python_path, "-m", "venv", venv_path])
        # Activate the virtual environment - for macOS
        activate_command = f"source {venv_path}/bin/activate"
        subprocess.run(["bash", "-c", activate_command])

    def install_pyenv(self):
        # Example command, adjust based on OS
        subprocess.run(["curl", "-L", "https://pyenv.run", "|", "bash"])
        # Additional commands may be needed to integrate pyenv into the shell

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

    def create_briefcase_project(self):
        # Create a new project using Briefcase
        pass

    def setup_venv(self):
        # Create a virtual environment using the Python version installed by pyenv
        # Example: subprocess.run([f'{pyenv_root}/versions/3.9.1/bin/python', '-m', 'venv', 'env'])
        pass

    def install_dependencies(self):
        # Modify pyproject.toml and install dependencies
        pass

    def create_pyproject_file(self, user_data):
        # Construct the path to the template file in the resources directory
        template_file_name = "base_project_template.toml"
        template_path = (
            self.main_window.app.resource_path / "resources" / template_file_name
        )

        # New project file path
        new_project_path = os.path.join(
            self.project_folder, user_data["app_name"], "pyproject.toml"
        )

        with open(template_path, "r") as template_file:
            template_content = template_file.read()

        # Replace placeholders with actual data
        for key, value in user_data.items():
            placeholder = "{{" + key.upper() + "}}"
            template_content = template_content.replace(placeholder, value)

        # Write the new pyproject.toml file
        with open(new_project_path, "w") as new_project_file:
            new_project_file.write(template_content)


def main():
    return NADOOLaunchpad()
