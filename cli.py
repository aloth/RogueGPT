#!/usr/bin/env python3
"""Source-checkout shim so `python3 cli.py <command>, as documented in the JOSS paper` keeps working.

The code lives in the roguegpt package; installed users run the console scripts instead.
"""

from roguegpt.cli import main

if __name__ == "__main__":
    main()
