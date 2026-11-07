#!/usr/bin/env python3
"""Source-checkout shim so `python3 generate_batch.py` keeps working.

The code lives in the roguegpt package; installed users run the console scripts instead.
"""

from roguegpt.generate_batch import main

if __name__ == "__main__":
    main()
