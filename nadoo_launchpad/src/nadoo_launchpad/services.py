from typing import Dict
import briefcase
import toga
import toml
#from nadoo_launchpad.models import Developer
from nadoo_launchpad.utils import *



def check_installation_state(app:toga.App):
    # Check the config file for the installation state
    config_path = app.paths.config / "install_state.toml"
    if config_path.exists():
        with open(config_path, "r") as config_file:
            config_data = toml.load(config_file)
        return config_data.get("installed", False)
    return False

def install(self:toga.Box, app):
    # Installation logic
    # Update installation state in config file
    set_installation_state()
    project_folder = setup_project_folder()
    install_pyenv()
    install_python_with_pyenv()
    set_installation_state()

    # Correctly initialize ProjectInfoComponent
    #project_info_component = ProjectInfoComponent(self.app)

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

    # The class name can be completely derived from the formal name.
    from briefcase.config import make_class_name, is_valid_app_name

    formal_name = self.project_name_input.value
    class_name = make_class_name(formal_name)

    # Check if the app name is valid
    app_name = make_app_name(formal_name)
    if not is_valid_app_name(app_name):
        # If not valid, display the error using display_error
        error_message = (
            f"'{app_name}' is not a valid app name. Please choose a different name."
        )
        self.app.display_error(error_message)
        return

    # The module name can be completely derived from the app name.
    module_name = make_module_name(app_name)

    context = {
        "formal_name": formal_name,  # Assuming formal_name is the same as project_name
        "app_name": app_name,  # Assuming app_name is a lowercase, underscored version of project_name
        "class_name": class_name,
        "module_name": module_name,
        "project_name": self.project_name_input.value,
        "description": self.description_input.value,
        "author": self.author_input.value,
        "author_email": self.author_email_input.value,
        "bundle": self.bundle_input.value,
        "url": self.url_input.value,
        "license": self.license_dropdown.value,
        "gui_framework": self.gui_framework_dropdown.value,
    }
    # If a branch wasn't supplied through the --template-branch argument,
    # use the branch derived from the Briefcase version
    version = Version(briefcase.__version__)

    branch = f"v{version.base_version}"

    # Get the project folder path as a Path object
    project_folder_path = Path(get_project_folder_path())

    # Ensure context["app_name"] is a string
    app_name = str(context["app_name"])

    # Construct the path to the new app's directory
    new_app_path = project_folder_path / app_name

    # Make extra sure we won't clobber an existing application.
    if new_app_path.exists():
        self.app.display_error(
            f"A directory named '{context['app_name']}' already exists."
        )

    # project_template = self.create_pyproject_file(user_data, project_folder)

    # Step 5: Use Briefcase to create a new project

    template = "git@github.com:NADOOIT/batteries-included-briefcase-template.git"

    # Additional context for the Briefcase template pyproject.toml header to
    # include the version of Briefcase as well as the source of the template.
    context.update(
        {
            "template_source": template,
            "template_branch": branch,
            "briefcase_version": briefcase.__version__,
        }
    )

    # briefcase_path = os.path.join(venv_path, "bin", "briefcase")
    # briefcase_command = [briefcase_path, "new", "--template", template]
    # subprocess.run(briefcase_command, cwd=project_folder)

    try:
        # Unroll the new app template
        generate_template(
            template=template,
            branch=branch,
            output_path=get_project_folder_path(),
            extra_context=context,
        )
    except TemplateUnsupportedVersion:
        # If we're *not* on a development branch, raise an error about
        # the missing template branch.
        if version.dev is None:
            raise

        # Development branches can use the main template.
        self.logger.info(
            f"Template branch {branch} not found; falling back to development template"
        )
        branch = "main"
        generate_template(
            template=template,
            branch=branch,
            output_path=get_project_folder_path(),
            extra_context=context,
        )

def cancel_action(self:toga.App):
    # Restore initial values
    if self.app.main_box:
        self.app.main_box.children.pop()