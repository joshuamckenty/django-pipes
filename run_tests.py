#! /usr/bin/env python
if __name__ == "__main__":
    import os
    if "DJANGO_SETTINGS_MODULE" not in os.environ:
        parser.error("Environment variable DJANGO_SETTINGS_MODULE is not set. Set it to a test project to run the tests.")
        sys.exit(0)
    import nose
    nose.main()
