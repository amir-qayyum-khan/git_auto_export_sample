from django.utils.translation import ugettext_lazy as _

from utils import GIT_REPO_EXPORT_DIR


class GitExportError(Exception):
    """
    Convenience exception class for git export error conditions.
    """

    def __init__(self, message):
        # Force the lazy i18n values to turn into actual unicode objects
        super(GitExportError, self).__init__(unicode(message))

    NO_EXPORT_DIR = _("GIT_REPO_EXPORT_DIR not set or path {0} doesn't exist, "
                      "please create it, or configure a different path with "
                      "GIT_REPO_EXPORT_DIR").format(GIT_REPO_EXPORT_DIR)
    URL_BAD = _('Non writable git url provided. Expecting something like:'
                ' git@github.com:mitocw/edx4edx_lite.git')
    URL_NO_AUTH = _('If using http urls, you must provide the username '
                    'and password in the url. Similar to '
                    'https://user:pass@github.com/user/course.')
    DETACHED_HEAD = _('Unable to determine branch, repo in detached HEAD mode')
    CANNOT_PULL = _('Unable to update or clone git repository.')
    XML_EXPORT_FAIL = _('Unable to export course to xml.')
    CONFIG_ERROR = _('Unable to configure git username and password')
    CANNOT_COMMIT = _('Unable to commit changes. This is usually '
                      'because there are no changes to be committed')
    CANNOT_PUSH = _('Unable to push changes.  This is usually '
                    'because the remote repository cannot be contacted')
    BAD_COURSE = _('Bad course location provided')
    MISSING_BRANCH = _('Missing branch on fresh clone')
