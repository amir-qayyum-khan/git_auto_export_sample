"""This module has version code and code for running auto export task"""
import logging
from django.conf import settings
from django.core.files.storage import default_storage
from tasks import async_export_to_git


log = logging.getLogger(__name__)
__version__ = 0.1
GIT_REPO_EXPORT_DIR = getattr(settings, 'GIT_REPO_EXPORT_DIR', '/edx/var/edxapp/export_course_repos')

if not default_storage.exists(GIT_REPO_EXPORT_DIR):
    # if folder does not exist create it
    log.error("GIT_REPO_EXPORT_DIR is not available, please create it first")


def run_auto_git_export(course_key):
    """
    If the Git auto-export is enabled, push the course changes to Git

    Args:
        course_key (CourseKey): edX course key
    """
    if settings.FEATURES.get('ENABLE_EXPORT_GIT') and settings.FEATURES.get('ENABLE_GIT_AUTO_EXPORT'):
        log.info(
            'Course published with auto-export enabled. Starting export... (course id: %s)', course_key
        )
        async_export_to_git.delay(unicode(course_key))
