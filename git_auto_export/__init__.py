"""This module has version code and code for running auto export task"""
import logging
from django.conf import settings
from tasks import async_export_to_git


log = logging.getLogger(__name__)
__version__ = 0.1


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
