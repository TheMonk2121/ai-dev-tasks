#!/usr/bin/env python3
import sys

print("[DEPRECATION] Use evals_300.tools.run; forwarding…")
from evals_300.tools.run import main as ssot_main

if __name__ == "__main__":
    sys.exit(ssot_main())

