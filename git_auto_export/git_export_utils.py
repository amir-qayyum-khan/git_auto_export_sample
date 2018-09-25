import logging
import os
import subprocess
from urlparse import urlparse

from django.contrib.auth.models import User
from django.utils import timezone

from xmodule.contentstore.django import contentstore
from xmodule.modulestore.django import modulestore
from xmodule.modulestore.xml_exporter import export_course_to_xml

from exception import GitExportError

log = logging.getLogger(__name__)


def cmd_log(cmd, cwd):
    """
    Helper function to redirect stderr to stdout and log the command
    used along with the output. Will raise subprocess.CalledProcessError if
    command doesn't return 0, and returns the command's output.
    """
    output = subprocess.check_output(cmd, cwd=cwd, stderr=subprocess.STDOUT)
    log.debug('Command was: {0!r}. '
              'Working directory was: {1!r}'.format(' '.join(cmd), cwd))
    log.debug('Command output was: {0!r}'.format(output))
    return output


def export_to_git(course_id, repo, user='', rdir=None):
    """Export a course to git."""
    from utils import GIT_REPO_EXPORT_DIR, GIT_EXPORT_DEFAULT_IDENT
    # pylint: disable=too-many-statements
    log.info("Starting git export (course id: %s)", course_id)

    if not GIT_REPO_EXPORT_DIR:
        raise GitExportError(GitExportError.NO_EXPORT_DIR)

    if not os.path.isdir(GIT_REPO_EXPORT_DIR):
        raise GitExportError(GitExportError.NO_EXPORT_DIR)

    # Check for valid writable git url
    if not (repo.endswith('.git') or
            repo.startswith(('http:', 'https:', 'file:'))):
        raise GitExportError(GitExportError.URL_BAD)

    # Check for username and password if using http[s]
    if repo.startswith('http:') or repo.startswith('https:'):
        parsed = urlparse(repo)
        if parsed.username is None or parsed.password is None:
            raise GitExportError(GitExportError.URL_NO_AUTH)
    if rdir:
        rdir = os.path.basename(rdir)
    else:
        rdir = repo.rsplit('/', 1)[-1].rsplit('.git', 1)[0]

    log.debug("rdir = %s", rdir)

    # Pull or clone repo before exporting to xml
    # and update url in case origin changed.
    rdirp = '{0}/{1}'.format(GIT_REPO_EXPORT_DIR, rdir)
    branch = None
    if os.path.exists(rdirp):
        log.info('Directory already exists, doing a git reset and pull '
                 'instead of git clone.')
        cwd = rdirp
        # Get current branch
        cmd = ['git', 'symbolic-ref', '--short', 'HEAD']
        try:
            branch = cmd_log(cmd, cwd).strip('\n')
        except subprocess.CalledProcessError as ex:
            log.exception('Failed to get branch: %r', ex.output)
            raise GitExportError(GitExportError.DETACHED_HEAD)

        cmds = [
            ['git', 'remote', 'set-url', 'origin', repo],
            ['git', 'fetch', 'origin'],
            ['git', 'reset', '--hard', 'origin/{0}'.format(branch)],
            ['git', 'pull'],
            ['git', 'clean', '-d', '-f'],
        ]
    else:
        cmds = [['git', 'clone', repo]]
        cwd = GIT_REPO_EXPORT_DIR

    cwd = os.path.abspath(cwd)
    for cmd in cmds:
        try:
            cmd_log(cmd, cwd)
        except subprocess.CalledProcessError as ex:
            log.exception('Failed to pull git repository: %r', ex.output)
            raise GitExportError(GitExportError.CANNOT_PULL)

    # export course as xml before commiting and pushing
    root_dir = os.path.dirname(rdirp)
    course_dir = os.path.basename(rdirp).rsplit('.git', 1)[0]
    try:
        export_course_to_xml(modulestore(), contentstore(), course_id,
                             root_dir, course_dir)
    except (EnvironmentError, AttributeError):
        log.exception('Failed export to xml')
        raise GitExportError(GitExportError.XML_EXPORT_FAIL)

    # Get current branch if not already set
    if not branch:
        cmd = ['git', 'symbolic-ref', '--short', 'HEAD']
        try:
            branch = cmd_log(cmd, os.path.abspath(rdirp)).strip('\n')
        except subprocess.CalledProcessError as ex:
            log.exception('Failed to get branch from freshly cloned repo: %r',
                          ex.output)
            raise GitExportError(GitExportError.MISSING_BRANCH)

    # Now that we have fresh xml exported, set identity, add
    # everything to git, commit, and push to the right branch.
    ident = {}
    try:
        user = User.objects.get(username=user)
        ident['name'] = user.username
        ident['email'] = user.email
    except User.DoesNotExist:
        # That's ok, just use default ident
        ident = GIT_EXPORT_DEFAULT_IDENT
    time_stamp = timezone.now()
    cwd = os.path.abspath(rdirp)
    commit_msg = "Export from Studio at {time_stamp}".format(
        time_stamp=time_stamp,
    )
    try:
        cmd_log(['git', 'config', 'user.email', ident['email']], cwd)
        cmd_log(['git', 'config', 'user.name', ident['name']], cwd)
    except subprocess.CalledProcessError as ex:
        log.exception('Error running git configure commands: %r', ex.output)
        raise GitExportError(GitExportError.CONFIG_ERROR)
    try:
        cmd_log(['git', 'add', '.'], cwd)
        cmd_log(['git', 'commit', '-a', '-m', commit_msg], cwd)
    except subprocess.CalledProcessError as ex:
        log.exception('Unable to commit changes: %r', ex.output)
        raise GitExportError(GitExportError.CANNOT_COMMIT)
    try:
        cmd_log(['git', 'push', '-q', 'origin', branch], cwd)
    except subprocess.CalledProcessError as ex:
        log.exception('Error running git push command: %r', ex.output)
        raise GitExportError(GitExportError.CANNOT_PUSH)

    log.info("Finished git export (course id: %s)", course_id)