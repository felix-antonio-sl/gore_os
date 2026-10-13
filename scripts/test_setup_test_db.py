"""Protección de preparación de DB con Docker y SQL sintéticos; no conecta servicios."""
import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

SOURCE = Path(__file__).with_name("setup_test_db.sh")

class SetupTestDatabase(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory(prefix="gore-db-guard-")
        self.addCleanup(self.scratch.cleanup)
        root = Path(self.scratch.name)
        self.script = root / "scripts/setup_test_db.sh"
        self.script.parent.mkdir()
        source = Path(os.environ.get("FIXTURE_GORE_SCRIPT", str(SOURCE)))
        shutil.copy2(source, self.script)
        sql = root / "model/model_goreos/sql"
        sql.mkdir(parents=True)
        block = re.search(r"sql_files=\((.*?)\)", source.read_text(), re.S).group(1)
        for name in block.split():
            (sql / name).write_text("-- synthetic fixture\n")
        binary = root / "bin"
        binary.mkdir()
        docker = binary / "docker"
        docker.write_text('#!/usr/bin/env python3\nimport json,os,sys\n'
            'args=sys.argv[1:]\n'
            'with open(os.environ["FIXTURE_DOCKER_LOG"],"a") as f: f.write(json.dumps(args)+"\\n")\n'
            'if args[:2]==["container","inspect"]: print("true");sys.exit(0)\n'
            'sql=args[args.index("-c")+1] if "-c" in args else ""\n'
            'if sql.startswith("DROP DATABASE"):\n'
            ' print("synthetic database busy",file=sys.stderr);sys.exit(7)\n'
            'sys.exit(0)\n')
        docker.chmod(0o755)
        self.log = root / "docker.jsonl"
        self.env = {"PATH": f"{binary}:{os.defpath}", "FIXTURE_DOCKER_LOG": str(self.log)}

    def run_script(self, *args):
        return subprocess.run(["bash", str(self.script), *args], env=self.env,
                              capture_output=True, text=True, timeout=10)

    def test_no_implicit_shared_database_reset(self):
        result = self.run_script()
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.log.exists())

    def test_non_test_name_is_rejected_before_docker(self):
        result = self.run_script("fixture-container", "production", "fixture_owner")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.log.exists())

    def test_busy_database_is_not_forced_and_stops_before_create_or_seed(self):
        result = self.run_script("fixture-container", "owned_fixture_test", "fixture_owner")
        self.assertNotEqual(result.returncode, 0)
        calls = [json.loads(x) for x in self.log.read_text().splitlines()]
        drops = [x[x.index("-c")+1] for x in calls if "-c" in x]
        self.assertEqual(len(drops), 1)
        self.assertIn('DROP DATABASE IF EXISTS "owned_fixture_test";', drops[0])
        self.assertNotIn("FORCE", drops[0])
        self.assertFalse(any("CREATE DATABASE" in " ".join(x) for x in calls))
        self.assertFalse(any("-i" in x for x in calls))

if __name__ == "__main__":
    unittest.main()
