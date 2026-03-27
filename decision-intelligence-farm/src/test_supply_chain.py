import unittest

from supply_chain import PackageEntry, SupplyChainManager, VulnerabilityFinding


class SupplyChainManagerTest(unittest.TestCase):
    def test_generate_sbom(self):
        packages = [PackageEntry(name="pydantic", version="2.9.0", license="MIT")]
        sbom = SupplyChainManager.generate_sbom(packages, "farm")
        self.assertEqual(sbom["spdxVersion"], "SPDX-2.3")
        self.assertEqual(sbom["name"], "farm")
        self.assertEqual(len(sbom["packages"]), 1)

    def test_vulnerability_sla(self):
        findings = [
            VulnerabilityFinding(package="x", severity="critical", opened_at="2020-01-01"),
            VulnerabilityFinding(package="y", severity="high", opened_at="2020-01-01"),
        ]
        verdict = SupplyChainManager.evaluate_vulnerability_sla(
            findings, max_open_days_critical=7
        )
        self.assertFalse(verdict["passed"])
        self.assertEqual(len(verdict["breaches"]), 1)


if __name__ == "__main__":
    unittest.main()
