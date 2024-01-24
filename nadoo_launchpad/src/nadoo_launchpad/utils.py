import os
import platform
import re
import unicodedata
import subprocess
from briefcase.exceptions import (
    InvalidTemplateRepository,
    NetworkFailure,
    TemplateUnsupportedVersion,
    BriefcaseCommandError,
)
from cookiecutter import exceptions as cookiecutter_exceptions
from cookiecutter.main import cookiecutter
from cookiecutter.repository import is_repo_url
from pathlib import Path
import toga
import toml

cookiecutter = staticmethod(cookiecutter)

def make_app_name(formal_name):
    """Construct a candidate app name from a formal name.

    :param formal_name: The formal name
    :returns: The candidate app name
    """
    normalized = unicodedata.normalize("NFKD", formal_name)
    stripped = re.sub("[^0-9a-zA-Z_]+", "", normalized).lstrip("_")
    if stripped:
        return stripped.lower()
    else:
        # If stripping removes all the content,
        # use a dummy app name as the suggestion.
        return "myapp"


def make_module_name(app_name):
    """Construct a valid module name from an app name.

    :param app_name: The app name
    :returns: The app's module name.
    """
    return app_name.replace("-", "_")


def generate_template(template, branch, output_path, extra_context):
    """Ensure the named template is up-to-date for the given branch, and roll out
    that template.

    :param template: The template URL or path to generate
    :param branch: The branch of the template to use
    :param output_path: The filesystem path where the template will be generated.
    :param extra_context: Extra context to pass to the cookiecutter template
    """
    # Make sure we have an updated cookiecutter template,
    # checked out to the right branch
    cached_template = update_cookiecutter_cache(template=template, branch=branch)

    try:
        # Unroll the template
        cookiecutter(
            str(cached_template),
            no_input=True,
            output_dir=str(output_path),
            checkout=branch,
            extra_context=extra_context,
        )
    except subprocess.CalledProcessError as e:
        # Computer is offline
        # status code == 128 - certificate validation error.
        raise NetworkFailure("clone template repository") from e
    except cookiecutter_exceptions.RepositoryNotFound as e:
        # Either the template path is invalid,
        # or it isn't a cookiecutter template (i.e., no cookiecutter.json)
        raise InvalidTemplateRepository(template) from e
    except cookiecutter_exceptions.RepositoryCloneFailed as e:
        # Branch does not exist.
        raise TemplateUnsupportedVersion(branch) from e


def update_cookiecutter_cache(template: str, branch="master"):
    """Ensure that we have a current checkout of a template path.

    If the path is a local path, use the path as is.

    If the path is a URL, look for a local cache; if one exists, update it,
    including checking out the required branch.

    :param template: The template URL or path.
    :param branch: The template branch to use. Default: ``master``
    :return: The path to the cached template. This may be the originally
        provided path if the template was a file path.
    """
    if is_repo_url(template):
        # The app template is a repository URL.
        #
        # When in `no_input=True` mode, cookiecutter deletes and reclones
        # a template directory, rather than updating the existing repo.
        #
        # Look for a cookiecutter cache of the template; if one exists,
        # try to update it using git. If no cache exists, or if the cache
        # directory isn't a git directory, or git fails for some reason,
        # fall back to using the specified template directly.
        cached_template = cookiecutter_cache_path(template)
        try:
            repo = self.tools.git.Repo(cached_template)
            # Raises ValueError if "origin" isn't a valid remote
            remote = repo.remote(name="main")
            try:
                # Attempt to update the repository
                remote.fetch()
            except self.tools.git.exc.GitCommandError as e:
                # We are offline, or otherwise unable to contact
                # the origin git repo. It's OK to continue; but
                # capture the error in the log and warn the user
                # that the template may be stale.
                pass

            try:
                # Check out the branch for the required version tag.
                head = remote.refs[branch]

                self.logger.info(
                    f"Using existing template (sha {head.commit.hexsha}, "
                    f"updated {head.commit.committed_datetime.strftime('%c')})"
                )
                head.checkout()
            except IndexError as e:
                # No branch exists for the requested version.
                raise TemplateUnsupportedVersion(branch) from e
        except self.tools.git.exc.NoSuchPathError:
            # Template cache path doesn't exist.
            # Just use the template directly, rather than attempting an update.
            cached_template = template
        except self.tools.git.exc.InvalidGitRepositoryError:
            # Template cache path exists, but isn't a git repository
            # Just use the template directly, rather than attempting an update.
            cached_template = template
        except ValueError as e:
            raise BriefcaseCommandError(
                f"Git repository in a weird state, delete {cached_template} and try briefcase create again"
            ) from e
    else:
        # If this isn't a repository URL, treat it as a local directory
        cached_template = template

    return cached_template


def cookiecutter_cache_path(template):
    """Determine the cookiecutter template cache directory given a template URL.

    This will return a valid path, regardless of whether `template`

    :param template: The template to use. This can be a filesystem path or
        a URL.
    :returns: The path that cookiecutter would use for the given template name.
    """
    template = template.rstrip("/")
    tail = template.split("/")[-1]
    cache_name = tail.rsplit(".git")[0]
    return Path.home() / ".cookiecutters" / cache_name

def update_ui(self:toga.App):
    # Refresh the UI to show changes
    self.main_window.content = self.new_project_form

def set_installation_state(self:toga.Box):
    config_path = self.app.paths.config / "install_state.toml"

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

def update_ui_post_install(self:toga.App):
    # Remove the 'Install' button and add the 'New Project' button
    self.main_box.remove(self.install_btn)

def install_python_with_pyenv():
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

def install_pyenv():
    # Example command, adjust based on OS
    subprocess.run(["curl", "-L", "https://pyenv.run", "|", "bash"])
    # Additional commands may be needed to integrate pyenv into the shell

def setup_project_folder():
    # Get the current user's home directory and set the project folder path
    project_folder = get_project_folder_path()
    return project_folder

def get_project_folder_path():
    home_dir = os.path.expanduser("~")
    project_folder = os.path.join(home_dir, "Documents", "GitHub")

    # Create the folder if it doesn't exist
    if not os.path.exists(project_folder):
        os.makedirs(project_folder)

    return project_folder

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

def on_new_developer_name_entered(self, widget):
    # Generate the email based on the entered name
    new_name = widget.value
    if new_name:
        new_email = f"{new_name.replace(' ', '.').lower()}@nadooit.de"
        self.author_email_input.value = new_email

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