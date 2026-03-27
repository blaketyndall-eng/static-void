"""Sprint 2 quality gates and release-readiness checks."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class RiskTier(str, Enum):
    CORE = "core"
    MODERATE = "moderate"
    LOW = "low"


@dataclass
class ChangeEnvelope:
    """Normalized metadata about a proposed merge or release."""

    risk_tier: RiskTier
    tests_passed: bool
    lint_passed: bool
    build_passed: bool
    observability_verified: bool = False
    rollback_validated: bool = False
    critical_regression_tests_passed: bool = False
    security_scan_passed: bool = True


@dataclass
class GateResult:
    """Result object for CI/release quality gate evaluation."""

    passed: bool
    failed_checks: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class QualityGatePolicy:
    """Policy engine for tiered pre-merge and pre-release checks."""

    REQUIRED_BY_TIER = {
        RiskTier.CORE: (
            "tests_passed",
            "lint_passed",
            "build_passed",
            "observability_verified",
            "rollback_validated",
            "critical_regression_tests_passed",
            "security_scan_passed",
        ),
        RiskTier.MODERATE: (
            "tests_passed",
            "lint_passed",
            "build_passed",
            "observability_verified",
            "security_scan_passed",
        ),
        RiskTier.LOW: (
            "tests_passed",
            "lint_passed",
            "build_passed",
        ),
    }

    @classmethod
    def evaluate(cls, envelope: ChangeEnvelope) -> GateResult:
        required = cls.REQUIRED_BY_TIER[envelope.risk_tier]
        failed = [name for name in required if not getattr(envelope, name)]

        warnings: list[str] = []
        if envelope.risk_tier is RiskTier.LOW and not envelope.security_scan_passed:
            warnings.append("security_scan_passed=false on LOW tier; review manually")

        return GateResult(passed=not failed, failed_checks=failed, warnings=warnings)

    @classmethod
    def release_checklist(cls, envelope: ChangeEnvelope) -> dict:
        """Human-readable release checklist snapshot."""
        return {
            "risk_tier": envelope.risk_tier.value,
            "checks": {
                "tests": envelope.tests_passed,
                "lint": envelope.lint_passed,
                "build": envelope.build_passed,
                "observability": envelope.observability_verified,
                "rollback": envelope.rollback_validated,
                "critical_regressions": envelope.critical_regression_tests_passed,
                "security_scan": envelope.security_scan_passed,
            },
        }
