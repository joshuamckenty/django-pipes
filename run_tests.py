#! /usr/bin/env python
if __name__ == "__main__":
    import os
    if "DJANGO_SETTINGS_MODULE" not in os.environ:
        parser.error("DJANGO_SETTINGS_MODULE is not set in the environment. "
                      "Set it or use --settings.")
        sys.exit(1)
    import nose
    nose.main()
