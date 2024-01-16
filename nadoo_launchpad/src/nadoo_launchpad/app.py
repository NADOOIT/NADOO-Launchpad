import platform
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
import subprocess
import os
import sys


class NADOOLaunchpad(toga.App):
    def startup(self):
        self.main_box = toga.Box(style=Pack(direction=COLUMN))

        self.install_btn = toga.Button("Install", on_press=self.install)
        self.main_box.add(self.install_btn)

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

    # ... [rest of your methods]

    def create_new_project(self, widget):
        self.new_project_form = toga.Box(style=Pack(direction=COLUMN))

        # Add input fields
        self.project_name_input = toga.TextInput(placeholder="Project Name")
        self.bundle_input = toga.TextInput(placeholder="Bundle Identifier")
        # Add more fields as needed...

        # Add buttons
        cancel_btn = toga.Button("Cancel", on_press=self.cancel_new_project)
        add_project_btn = toga.Button("Add Project", on_press=self.add_new_project)
        button_box = toga.Box(
            children=[cancel_btn, add_project_btn], style=Pack(direction=ROW)
        )

        self.new_project_form.add(self.project_name_input)
        self.new_project_form.add(self.bundle_input)
        # Add more fields to the form...
        self.new_project_form.add(button_box)

        self.main_window.content = self.new_project_form

    def cancel_new_project(self, widget):
        # Logic to handle cancellation
        self.main_window.content = self.main_box  # Go back to the main screen

    def add_new_project(self, widget):
        # Collect data from form
        project_name = self.project_name_input.value
        bundle_identifier = self.bundle_input.value
        # Collect more data as needed...

        # Create project folder
        project_folder = os.path.join(self.project_folder, project_name)
        os.makedirs(project_folder, exist_ok=True)

        # Create and activate virtual environment
        venv_path = os.path.join(project_folder, f"{project_name}_venv")
        subprocess.run([sys.executable, "-m", "venv", venv_path])

        # Install Briefcase in the virtual environment
        pip_path = os.path.join(venv_path, "bin", "pip")
        subprocess.run([pip_path, "install", "briefcase"])

        # Execute briefcase new command with collected settings
        briefcase_path = os.path.join(venv_path, "bin", "briefcase")
        briefcase_command = [
            briefcase_path,
            "new",
            "--name",
            project_name,
            "--bundle",
            bundle_identifier,
            "--project-name",
            project_name,  # Assuming project name is same as project_name
            "--description",
            "A description",  # Replace with actual description or form input
            "--author",
            "Author Name",  # Replace with actual author or form input
            "--author-email",
            "author@example.com",  # Replace with actual email or form input
            "--url",
            "https://example.com",  # Replace with actual URL or form input
            "--license",
            "Proprietary",  # Replace with actual license or form input
            "--template",
            "toga",  # Replace with actual GUI framework or form input
        ]
        subprocess.run(briefcase_command, cwd=project_folder)

    def check_installation_state(self):
        config_path = os.path.join(self.setup_project_folder(), "install_state.conf")
        return os.path.exists(config_path)

    def set_installation_state(self):
        config_path = os.path.join(self.setup_project_folder(), "install_state.conf")
        with open(config_path, "w") as config_file:
            config_file.write("installed")

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


def main():
    return NADOOLaunchpad()
