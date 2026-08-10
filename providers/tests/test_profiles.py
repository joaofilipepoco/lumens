from pathlib import Path
import subprocess
import sys


def test_profiles_validate_without_resolving_credentials() -> None:
    result = subprocess.run(
        [sys.executable, "providers/validate_profiles.py"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "credentials" in result.stdout
