import unittest, yaml
from pathlib import Path

class ScopeRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root=Path(__file__).resolve().parents[1]
        cls.data=yaml.safe_load((root/"registry/control_scope_registry.yaml").read_text(encoding="utf-8"))
    def test_80_controls(self):
        self.assertEqual(80,len(self.data["controls"]))
    def test_unique_ids(self):
        ids=[x["control_id"] for x in self.data["controls"]]
        self.assertEqual(len(ids),len(set(ids)))
    def test_key_scope_examples(self):
        d={x["control_id"]:x["scope"] for x in self.data["controls"]}
        self.assertEqual("REPOSITORY",d["EMS-CTRL-011"])
        self.assertEqual("EMS",d["EMS-CTRL-067"])
        self.assertEqual("ORGANIZATION",d["EMS-CTRL-074"])
        self.assertEqual("EMS",d["EMS-CTRL-080"])

if __name__=="__main__":unittest.main()
