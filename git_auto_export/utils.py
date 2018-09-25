from django.conf import settings


GIT_REPO_EXPORT_DIR = getattr(settings, 'GIT_REPO_EXPORT_DIR', None)
GIT_EXPORT_DEFAULT_IDENT = getattr(settings, 'GIT_EXPORT_DEFAULT_IDENT',
                                   {'name': 'STUDIO_EXPORT_TO_GIT',
                                    'email': 'STUDIO_EXPORT_TO_GIT@example.com'})

