"""Validate that every pinned requirement has a portable wheel.

Usage: python scripts/build_manifest.py dist/wheels dist/wheels.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from packaging.requirements import Requirement
from packaging.utils import canonicalize_name, parse_wheel_filename

PYODIDE_VERSION = "0.29.5"
REQUIREMENTS = Path("wheel-requirements.txt")


def main(wheels_dir: Path, output: Path) -> None:
    expected: dict[str, str] = {}
    for raw_line in REQUIREMENTS.read_text(encoding="utf-8").splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line:
            continue
        requirement = Requirement(line)
        pinned = [s.version for s in requirement.specifier if s.operator == "=="]
        if len(pinned) != 1 or len(list(requirement.specifier)) != 1:
            raise ValueError(f"Each package must be pinned exactly once: {line}")
        expected[canonicalize_name(requirement.name)] = pinned[0]

    found: dict[str, str] = {}
    for wheel in sorted(wheels_dir.glob("*.whl")):
        name, version, _build, tags = parse_wheel_filename(wheel.name)
        name = canonicalize_name(name)
        if name not in expected:
            raise ValueError(f"Unexpected wheel: {wheel.name}")
        if str(version) != expected[name]:
            raise ValueError(f"Unexpected version for {name}: {version}")
        if not all(tag.abi == "none" and tag.platform == "any" for tag in tags):
            raise ValueError(f"Native wheel cannot be installed in Pyodide: {wheel.name}")
        if name in found:
            raise ValueError(f"Multiple wheels for package {name}")
        found[name] = wheel.name

    if set(found) != set(expected):
        raise ValueError(f"Missing wheels: {sorted(set(expected) - set(found))}")

    payload = {
        "pyodide_version": PYODIDE_VERSION,
        "wheels": [found[name] for name in expected],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Validated {len(found)} pure-Python wheels and wrote {output}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: build_manifest.py WHEELS_DIR OUTPUT_JSON")
    main(Path(sys.argv[1]), Path(sys.argv[2]))
