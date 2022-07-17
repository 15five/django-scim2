import os
import sys

def run_tests():
    os.environ['DJANGO_SETTINGS_MODULE'] = os.environ.get('DJANGO_SETTINGS_MODULE', 'tests.settings')

    import django
    django.setup()
    from django.test.utils import get_runner
    from django.conf import settings

    # eg. TEST_FILTER=tests.test_views.UserTestCase.test_get_user_by_id
    test_filter = os.environ.get('TEST_FILTER')
    test_labels = [test_filter] if test_filter else []

    test_runner = get_runner(settings)
    failures = test_runner(
        pattern='test_*.py',
        verbosity=1,
        interactive=True
    ).run_tests(test_labels)
    sys.exit(failures)
