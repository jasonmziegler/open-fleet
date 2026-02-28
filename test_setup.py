#!/usr/bin/env python3
"""
Validates that project setup is complete:
- All required packages importable
- Expected directory structure present
"""

import sys
import io
from pathlib import Path
from importlib.metadata import version as pkg_version

# Ensure stdout uses UTF-8 on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

FAILURES: list[str] = []


def check(label: str, condition: bool) -> None:
    status = "✅" if condition else "❌"
    print(f"{status} {label}")
    if not condition:
        FAILURES.append(label)


# --- Package Imports ---
print("\n=== Package Checks ===")

try:
    import slack_bolt  # noqa: F401
    check(f"slack-bolt ({pkg_version('slack-bolt')})", True)
except ImportError:
    check("slack-bolt", False)

try:
    import slack_sdk  # noqa: F401
    check(f"slack-sdk ({pkg_version('slack-sdk')})", True)
except ImportError:
    check("slack-sdk", False)

try:
    import googleapiclient  # noqa: F401
    check("google-api-python-client", True)
except ImportError:
    check("google-api-python-client", False)

try:
    import google_auth_oauthlib  # noqa: F401
    check("google-auth-oauthlib", True)
except ImportError:
    check("google-auth-oauthlib", False)

try:
    import google.genai  # noqa: F401
    check(f"google-genai ({pkg_version('google-genai')})", True)
except ImportError:
    check("google-genai", False)

try:
    import aiohttp
    check(f"aiohttp ({aiohttp.__version__})", True)
except ImportError:
    check("aiohttp", False)

try:
    import dotenv  # noqa: F401
    check("python-dotenv", True)
except ImportError:
    check("python-dotenv", False)

try:
    import pydantic
    check(f"pydantic ({pydantic.__version__})", True)
except ImportError:
    check("pydantic", False)

# --- Directory Structure ---
print("\n=== Directory Structure Checks ===")

root = Path(__file__).parent
required_dirs = [
    "src/open_fleet",
    "src/open_fleet/adapters",
    "src/open_fleet/adapters/slack",
    "src/open_fleet/core",
    "src/open_fleet/tools",
    "src/open_fleet/llm",
    "tests",
    "tests/test_core",
    "tests/test_tools",
    "tests/test_llm",
    "logs",
    "scripts",
]

for d in required_dirs:
    path = root / d
    check(f"Directory: {d}/", path.is_dir())

# --- Key Files ---
print("\n=== Key File Checks ===")

required_files = [
    "requirements.txt",
    "requirements-dev.txt",
    ".env.example",
    "start.bat",
    "src/open_fleet/__init__.py",
    "src/open_fleet/main.py",
]

for f in required_files:
    path = root / f
    check(f"File: {f}", path.is_file())

# --- Summary ---
print(f"\n{'=' * 40}")
if FAILURES:
    print(f"❌ {len(FAILURES)} check(s) failed:")
    for f in FAILURES:
        print(f"   - {f}")
    sys.exit(1)
else:
    print("🎉 All checks passed! Project scaffold complete.")
    sys.exit(0)
