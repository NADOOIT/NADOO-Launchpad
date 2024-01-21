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


def generate_template(self, template, branch, output_path, extra_context):
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
            remote = repo.remote(name="origin")
            try:
                # Attempt to update the repository
                remote.fetch()
            except self.tools.git.exc.GitCommandError as e:
                # We are offline, or otherwise unable to contact
                # the origin git repo. It's OK to continue; but
                # capture the error in the log and warn the user
                # that the template may be stale.
                self.logger.debug(str(e))
                self.logger.warning(
                    """
*************************************************************************
** WARNING: Unable to update template                                  **
*************************************************************************

Briefcase is unable the update the application template. This
may be because your computer is currently offline. Briefcase will
use existing template without updating.

*************************************************************************
"""
                )

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
