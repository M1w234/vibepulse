import argparse
import plistlib
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import install_macos


class InstallMacOSTests(unittest.TestCase):
    def _args(self, **overrides):
        values = dict(
            port=8737, github_repo=None, claude_plan=None, codex_plan=None,
            plan=[], interactions=False, interaction_detail=False,
        )
        values.update(overrides)
        return argparse.Namespace(**values)

    def test_plist_uses_current_checkout_and_python(self):
        result = install_macos.build_plist(
            self._args(), python_path=Path("/opt/homebrew/bin/python3"),
            tokenserver_dir=Path("/Users/michael/Code/VibePulse/tools/tokenserver"),
            home=Path("/Users/michael"),
        )
        self.assertEqual(result["WorkingDirectory"],
                         "/Users/michael/Code/VibePulse/tools/tokenserver")
        self.assertEqual(result["ProgramArguments"][:3], [
            "/opt/homebrew/bin/python3", "-u",
            "/Users/michael/Code/VibePulse/tools/tokenserver/tokenserver.py",
        ])
        self.assertNotIn("niclasvestlund", plistlib.dumps(result).decode())

    def test_optional_settings_become_launch_arguments(self):
        result = install_macos.build_plist(
            self._args(github_repo="M1w234/vibepulse", claude_plan="max20x",
                       codex_plan="pro", plan=["claude=200", "codex=20"],
                       interactions=True),
            python_path=Path("/usr/bin/python3"),
            tokenserver_dir=Path("/repo/tools/tokenserver"),
            home=Path("/Users/test"),
        )
        arguments = result["ProgramArguments"]
        self.assertIn("M1w234/vibepulse", arguments)
        self.assertIn("max20x", arguments)
        self.assertIn("pro", arguments)
        self.assertEqual(arguments.count("--plan"), 2)
        self.assertIn("--interactions", arguments)


if __name__ == "__main__":
    unittest.main()
