#!/usr/bin/env python3
"""Compatibility entry point; the specification repository has no production runtime."""
from repository_release_gate import main


if __name__ == "__main__":
    print("NOTICE=production_gate is deprecated; running repository_release_gate")
    raise SystemExit(main())
