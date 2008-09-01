#! /usr/bin/env python
if __name__ == "__main__":
    import os
    if "DJANGO_SETTINGS_MODULE" not in os.environ:
        print "Using pipes_sample as the test Django project..."
        os.environ['DJANGO_SETTINGS_MODULE'] = 'pipes_sample.settings'
    import nose
    nose.main()
