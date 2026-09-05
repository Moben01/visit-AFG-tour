from dataclasses import dataclass
from fnmatch import fnmatch
import re


@dataclass(frozen=True)
class LegacyBrandAllowlistRule:
    path_pattern: str
    category: str
    reason: str
    terms: tuple[str, ...] = ()
    line_pattern: str = ""

    def matches(self, path, term, line):
        if not fnmatch(path, self.path_pattern):
            return False
        if self.terms and term.casefold() not in {
            allowed.casefold() for allowed in self.terms
        }:
            return False
        return not self.line_pattern or bool(re.search(self.line_pattern, line))


LEGACY_BRAND_ALLOWLIST = (
    LegacyBrandAllowlistRule(
        "AGENTS.md",
        "historical_migration_documentation",
        "Repository policy records the prohibited legacy terms.",
    ),
    LegacyBrandAllowlistRule(
        "docs/relaunch/**",
        "historical_migration_documentation",
        "Relaunch audit and migration documentation is not rendered publicly.",
    ),
    LegacyBrandAllowlistRule(
        "afghanawaits-*.tar.gz",
        "non_rendered_infrastructure_record",
        "Root hotfix archives are internal deployment history and are never served as public static files.",
    ),
    LegacyBrandAllowlistRule(
        "**/migrations/**",
        "historical_migration_documentation",
        "Historical migrations are immutable and are not public content.",
    ),
    LegacyBrandAllowlistRule(
        "home/branding.py",
        "audit_implementation",
        "The scanner and replacement registry must define the prohibited terms.",
    ),
    LegacyBrandAllowlistRule(
        "home/legacy_brand_allowlist.py",
        "audit_implementation",
        "The explicit allowlist documents permitted internal occurrences.",
    ),
    LegacyBrandAllowlistRule(
        "home/management/commands/audit_legacy_branding.py",
        "audit_implementation",
        "The audit command reports the prohibited terms without rendering them.",
    ),
    LegacyBrandAllowlistRule(
        "home/management/commands/replace_legacy_branding.py",
        "audit_implementation",
        "The controlled replacement command consumes the prohibited-term registry.",
    ),
    LegacyBrandAllowlistRule(
        "**/test*.py",
        "test_fixture",
        "Automated negative tests intentionally contain prohibited input.",
    ),
    LegacyBrandAllowlistRule(
        "**/tests/**",
        "test_fixture",
        "Automated negative tests intentionally contain prohibited input.",
    ),
    LegacyBrandAllowlistRule(
        "visit_afg_core/settings.py",
        "legacy_hostname_redirect_configuration",
        "The old hostname remains accepted during the redirect transition.",
        terms=("AfghanAwaits", "AfghanAwaits.com"),
        line_pattern=r"AFGHANAWAITS_APP_ROOT|localhost,127\.0\.0\.1|https://afghanawaits\.com",
    ),
    LegacyBrandAllowlistRule(
        "home/models.py",
        "legacy_hostname_redirect_configuration",
        "The centralized configuration retains the old hostname for redirects.",
        terms=("AfghanAwaits.com",),
        line_pattern=r'default="afghanawaits\.com"',
    ),
    LegacyBrandAllowlistRule(
        "tour/signals.py",
        "non_rendered_infrastructure_record",
        "The stable onboarding course code is an internal identifier and is never rendered.",
        terms=("AfghanAwaits",),
        line_pattern=r"code=['\"]afghanawaits-onboarding['\"]",
    ),
)


def find_allowlist_rule(path, term, line):
    return next(
        (rule for rule in LEGACY_BRAND_ALLOWLIST if rule.matches(path, term, line)),
        None,
    )
