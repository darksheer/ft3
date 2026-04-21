"""
Tests for crosswalk/crosswalk.json — covering the F3-only reverse-coverage
rows introduced in Phase 1.5.

Run with:  python3 -m pytest tests/test_crosswalk.py -v
"""

import json
import pathlib
import re
import pytest

CROSSWALK_PATH = pathlib.Path(__file__).parent.parent / "crosswalk" / "crosswalk.json"

REQUIRED_FIELDS = {"confidence", "f3_id", "f3_name", "ft3_id", "ft3_name", "notes", "relationship"}
VALID_RELATIONSHIPS = {"equivalent", "derived", "unmapped"}
VALID_CONFIDENCE_LEVELS = {"exact", "none", "collision", "substring"}

# Canonical note text attached to every F3-only unmapped row added in this PR.
F3_ONLY_NOTE = "F3-only technique; no FT3 counterpart."

# Every f3_id that must be present as a result of this PR.  The list mirrors
# the diff exactly, preserving ordering so regression is easy to spot.
NEW_F3_ONLY_IDS = [
    "F1002", "F1003", "F1004",
    "F1005.001", "F1005.002",
    "F1006.001",
    "F1007", "F1007.001", "F1007.002", "F1007.003",
    "F1008", "F1008.001", "F1008.002",
    "F1009", "F1009.001", "F1009.002", "F1009.003", "F1009.004",
    "F1010", "F1011", "F1013", "F1014", "F1016",
    "F1017", "F1017.001", "F1017.002", "F1017.003",
    "F1018", "F1019",
    "F1020", "F1020.001", "F1020.002",
    "F1021", "F1022", "F1023", "F1024",
    "F1025", "F1025.001", "F1025.002", "F1025.003",
    "F1026", "F1027", "F1028", "F1029", "F1030",
    "F1031", "F1032", "F1033", "F1034", "F1035",
    "F1036", "F1037", "F1038", "F1039", "F1040",
    "F1040.001", "F1040.002",
    "F1041", "F1042", "F1043", "F1045", "F1046", "F1047", "F1048",
    "T1070",
    "T1110", "T1110.001", "T1110.002", "T1110.003", "T1110.004",
    "T1111", "T1113", "T1185", "T1189", "T1219",
    "T1451", "T1453", "T1539",
    "T1550", "T1550.001",
    "T1555", "T1555.003", "T1555.005",
    "T1557",
    "T1583", "T1583.001", "T1583.003", "T1583.008",
    "T1586.004",
    "T1593", "T1593.001", "T1593.002",
    "T1608", "T1608.006",
    "T1621", "T1667", "T1672",
]

# Expected (f3_id, f3_name) pairs for a representative subset of new entries.
NEW_F3_ONLY_NAMES = {
    "F1002": "Abuse of Public-Facing API",
    "F1003": "Abuse SMS verification",
    "F1004": "Access with Stolen Session Cookie",
    "F1005.001": "Account Manipulation: Account Linking",
    "F1005.002": "Account Manipulation: Add Authorized User",
    "F1006.001": "Account Takeover: Exposed API Key",
    "F1007": "Adversary-in-the-Browser",
    "F1007.001": "Adversary-in-the-Browser: DLL Injection",
    "F1007.002": "Adversary-in-the-Browser: Malicious Browser Extension",
    "F1007.003": "Adversary-in-the-Browser: Malicious JavaScript Injection",
    "F1008": "ATM Manipulation",
    "F1008.001": "ATM Manipulation: ATM Hardware Manipulation",
    "F1008.002": "ATM Manipulation: ATM Software Manipulation",
    "F1009": "Bank Deposit",
    "F1009.001": "Bank Deposit: ATM Deposit",
    "F1009.002": "Bank Deposit: Mobile Deposit",
    "F1009.003": "Bank Deposit: Night Deposit",
    "F1009.004": "Bank Deposit: Test Deposit",
    "F1010": "Buy Money Order",
    "F1011": "Card Dump Capture",
    "F1013": "Change Payroll Details",
    "F1014": "Check Fraud",
    "F1016": "Compromise Payment Gateway",
    "F1017": "Conversion to Physical Monetary Instruments",
    "F1017.001": "Conversion to Physical Monetary Instruments: Cash",
    "F1017.002": "Conversion to Physical Monetary Instruments: Cashier's Check",
    "F1017.003": "Conversion to Physical Monetary Instruments: Money Order",
    "F1018": "Convert to Cryptocurrency",
    "F1019": "Create Counterfeit Card",
    "F1020": "Create Fake Materials",
    "F1020.001": "Create Fake Materials: Fake Documents",
    "F1020.002": "Create Fake Materials: Fake Website",
    "F1021": "Create Fraudulent Merchant Account",
    "F1022": "Delete Relevant Emails",
    "F1023": "Device Fingerprint Spoofing",
    "F1024": "Dispute Legitimate Transaction",
    "F1025": "Electronic Funds Transfer",
    "F1025.001": "Electronic Funds Transfer: Peer-to-Peer Transfer",
    "F1025.002": "Electronic Funds Transfer: Regional Payment Rail",
    "F1025.003": "Electronic Funds Transfer: Wire Transfer",
    "F1026": "Exploitation of Gambling Platforms",
    "F1027": "Falsify Business Documents",
    "F1028": "Fradulent Purchasing",
    "F1029": "Gather Customer Information",
    "F1030": "Geolocation Spoofing",
    "F1031": "Impersonate Account Holder",
    "F1032": "Impersonate Official",
    "F1033": "Insider Access Abuse",
    "F1034": "Interactive Voice Response Mapping",
    "F1035": "Mail Theft",
    "F1036": "New Vendor Setup",
    "F1037": "NFC Payment",
    "F1038": "PAN/CVV Generation",
    "F1039": "PaReq Manipulation",
    "F1040": "Phone Number Spoofing",
    "F1040.001": "Phone Number Spoofing: Customer Phone Number Spoofing",
    "F1040.002": "Phone Number Spoofing: Official Phone Number Spoofing",
    "F1041": "PIN-code Peeking",
    "F1042": "Reactivate Account",
    "F1043": "Reversal of Transaction",
    "F1045": "Structuring",
    "F1046": "Test Payment Thresholds",
    "F1047": "Transfer of funds",
    "F1048": "Use Virtual Cards",
    "T1070": "Indicator Removal",
    "T1110": "Brute Force",
    "T1110.001": "Brute Force: Password Guessing",
    "T1110.002": "Brute Force: Password Cracking",
    "T1110.003": "Brute Force: Password Spraying",
    "T1110.004": "Brute Force:  Credential Stuffing",
    "T1111": "Multi-Factor Authentication Interception",
    "T1113": "Screen Capture",
    "T1185": "Browser Session Hijacking",
    "T1189": "Drive-by Compromise",
    "T1219": "Remote Access Tools",
    "T1451": "SIM Card Swap",
    "T1453": "Abuse Accessibility Features",
    "T1539": "Steal Web Session Cookie",
    "T1550": "Use Alternate Authentication Material",
    "T1550.001": "Use Alternate Authentication Material: Application Access Token",
    "T1555": "Credentials from Password Stores",
    "T1555.003": "Credentials from Password Stores: Credentials from Web Browsers",
    "T1555.005": "Credentials from Password Stores: Password Managers",
    "T1557": "Adversary-in-the-Middle",
    "T1583": "Acquire Infrastructure",
    "T1583.001": "Acquire Infrastructure: Domains",
    "T1583.003": "Acquire Infrastructure: Virtual Private Network or Server",
    "T1583.008": "Acquire Infrastructure: Malvertising",
    "T1586.004": "Compromise Accounts: Corporate Accounts",
    "T1593": "Search Open Websites/Domains",
    "T1593.001": "Search Open Websites/Domains: Social Media",
    "T1593.002": "Search Open Websites/Domains: Search Engines",
    "T1608": "Stage Capabilities",
    "T1608.006": "Stage Capabilities: SEO Poisoning",
    "T1621": "Multi-Factor Authentication Request Generation",
    "T1667": "Email Bombing",
    "T1672": "Email Spoofing",
}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def crosswalk():
    """Load and return the parsed crosswalk list once per test module."""
    raw = CROSSWALK_PATH.read_text(encoding="utf-8")
    return json.loads(raw)


@pytest.fixture(scope="module")
def f3_only_entries(crosswalk):
    """Return only the F3-only unmapped entries added in this PR."""
    return [
        e for e in crosswalk
        if e.get("relationship") == "unmapped"
        and e.get("f3_id") is not None
        and e.get("ft3_id") is None
    ]


@pytest.fixture(scope="module")
def entries_by_f3_id(crosswalk):
    """Return a dict mapping f3_id -> list[entry] for quick lookups."""
    result: dict[str, list] = {}
    for entry in crosswalk:
        fid = entry.get("f3_id")
        if fid is not None:
            result.setdefault(fid, []).append(entry)
    return result


# ---------------------------------------------------------------------------
# 1. File-level validity
# ---------------------------------------------------------------------------

class TestFileValidity:
    def test_file_exists(self):
        assert CROSSWALK_PATH.exists(), f"crosswalk.json not found at {CROSSWALK_PATH}"

    def test_is_valid_json(self):
        raw = CROSSWALK_PATH.read_text(encoding="utf-8")
        parsed = json.loads(raw)  # raises json.JSONDecodeError on failure
        assert parsed is not None

    def test_top_level_is_list(self, crosswalk):
        assert isinstance(crosswalk, list), "crosswalk.json must be a JSON array"

    def test_has_entries(self, crosswalk):
        assert len(crosswalk) > 0, "crosswalk.json must not be empty"


# ---------------------------------------------------------------------------
# 2. Schema / field presence
# ---------------------------------------------------------------------------

class TestSchema:
    def test_all_entries_have_required_fields(self, crosswalk):
        for i, entry in enumerate(crosswalk):
            missing = REQUIRED_FIELDS - set(entry.keys())
            assert not missing, (
                f"Entry {i} is missing fields {missing}: {entry}"
            )

    def test_no_extra_fields(self, crosswalk):
        for i, entry in enumerate(crosswalk):
            extra = set(entry.keys()) - REQUIRED_FIELDS
            assert not extra, (
                f"Entry {i} has unexpected extra fields {extra}: {entry}"
            )

    def test_relationship_field_is_string(self, crosswalk):
        for i, entry in enumerate(crosswalk):
            assert isinstance(entry["relationship"], str), (
                f"Entry {i} has non-string relationship: {entry['relationship']!r}"
            )

    def test_confidence_field_is_string(self, crosswalk):
        for i, entry in enumerate(crosswalk):
            assert isinstance(entry["confidence"], str), (
                f"Entry {i} has non-string confidence: {entry['confidence']!r}"
            )


# ---------------------------------------------------------------------------
# 3. Enumerated-value constraints
# ---------------------------------------------------------------------------

class TestEnumeratedValues:
    def test_relationship_values_are_valid(self, crosswalk):
        for i, entry in enumerate(crosswalk):
            assert entry["relationship"] in VALID_RELATIONSHIPS, (
                f"Entry {i} has invalid relationship {entry['relationship']!r}"
            )

    def test_confidence_values_are_valid(self, crosswalk):
        for i, entry in enumerate(crosswalk):
            assert entry["confidence"] in VALID_CONFIDENCE_LEVELS, (
                f"Entry {i} has invalid confidence {entry['confidence']!r}"
            )


# ---------------------------------------------------------------------------
# 4. Null-consistency rules
# ---------------------------------------------------------------------------

class TestNullConsistency:
    def test_f3_id_null_implies_f3_name_null(self, crosswalk):
        """If f3_id is null then f3_name must also be null."""
        for i, entry in enumerate(crosswalk):
            if entry["f3_id"] is None:
                assert entry["f3_name"] is None, (
                    f"Entry {i}: f3_id is null but f3_name is {entry['f3_name']!r}"
                )

    def test_f3_name_null_implies_f3_id_null(self, crosswalk):
        """If f3_name is null then f3_id must also be null."""
        for i, entry in enumerate(crosswalk):
            if entry["f3_name"] is None:
                assert entry["f3_id"] is None, (
                    f"Entry {i}: f3_name is null but f3_id is {entry['f3_id']!r}"
                )

    def test_ft3_id_null_implies_ft3_name_null(self, crosswalk):
        """If ft3_id is null then ft3_name must also be null."""
        for i, entry in enumerate(crosswalk):
            if entry["ft3_id"] is None:
                assert entry["ft3_name"] is None, (
                    f"Entry {i}: ft3_id is null but ft3_name is {entry['ft3_name']!r}"
                )

    def test_ft3_name_null_implies_ft3_id_null(self, crosswalk):
        """If ft3_name is null then ft3_id must also be null."""
        for i, entry in enumerate(crosswalk):
            if entry["ft3_name"] is None:
                assert entry["ft3_id"] is None, (
                    f"Entry {i}: ft3_name is null but ft3_id is {entry['ft3_id']!r}"
                )


# ---------------------------------------------------------------------------
# 5. Uniqueness constraints
# ---------------------------------------------------------------------------

class TestUniqueness:
    def test_new_f3_only_ids_are_unique_within_pr_entries(self, f3_only_entries):
        """Each F3-only ID added by this PR must appear exactly once among the
        F3-only unmapped rows — the design intentionally allows an f3_id to
        appear in multiple 'derived' rows (many-to-many FT3 mappings), but
        every F3-only reverse-coverage row must be a single, distinct record."""
        seen: dict[str, int] = {}
        for i, entry in enumerate(f3_only_entries):
            fid = entry["f3_id"]
            assert fid not in seen, (
                f"Duplicate f3_id {fid!r} in F3-only entries at positions "
                f"{seen[fid]} and {i}"
            )
            seen[fid] = i

    def test_non_null_ft3_ids_are_unique(self, crosswalk):
        seen: dict[str, int] = {}
        for i, entry in enumerate(crosswalk):
            fid = entry["ft3_id"]
            if fid is not None:
                assert fid not in seen, (
                    f"Duplicate ft3_id {fid!r} at indices {seen[fid]} and {i}"
                )
                seen[fid] = i


# ---------------------------------------------------------------------------
# 6. New F3-only unmapped entries — bulk properties
# ---------------------------------------------------------------------------

class TestNewF3OnlyEntries:
    def test_new_f3_only_entry_count(self, f3_only_entries):
        """Exactly 98 F3-only unmapped entries should be present after this PR."""
        assert len(f3_only_entries) == len(NEW_F3_ONLY_IDS), (
            f"Expected {len(NEW_F3_ONLY_IDS)} F3-only entries, found {len(f3_only_entries)}"
        )

    def test_all_f3_only_entries_relationship_is_unmapped(self, f3_only_entries):
        for entry in f3_only_entries:
            assert entry["relationship"] == "unmapped", (
                f"F3-only entry {entry['f3_id']!r} has unexpected relationship "
                f"{entry['relationship']!r}"
            )

    def test_all_f3_only_entries_confidence_is_none(self, f3_only_entries):
        for entry in f3_only_entries:
            assert entry["confidence"] == "none", (
                f"F3-only entry {entry['f3_id']!r} has confidence "
                f"{entry['confidence']!r}, expected 'none'"
            )

    def test_all_f3_only_entries_ft3_id_is_null(self, f3_only_entries):
        for entry in f3_only_entries:
            assert entry["ft3_id"] is None, (
                f"F3-only entry {entry['f3_id']!r} has non-null ft3_id "
                f"{entry['ft3_id']!r}"
            )

    def test_all_f3_only_entries_ft3_name_is_null(self, f3_only_entries):
        for entry in f3_only_entries:
            assert entry["ft3_name"] is None, (
                f"F3-only entry {entry['f3_id']!r} has non-null ft3_name "
                f"{entry['ft3_name']!r}"
            )

    def test_all_f3_only_entries_have_non_null_f3_id(self, f3_only_entries):
        for entry in f3_only_entries:
            assert entry["f3_id"] is not None

    def test_all_f3_only_entries_have_non_null_f3_name(self, f3_only_entries):
        for entry in f3_only_entries:
            assert entry["f3_name"] is not None, (
                f"F3-only entry with f3_id {entry['f3_id']!r} has null f3_name"
            )

    def test_all_f3_only_entries_notes_value(self, f3_only_entries):
        """Every new F3-only entry must carry the canonical notes string."""
        for entry in f3_only_entries:
            assert entry["notes"] == F3_ONLY_NOTE, (
                f"Entry {entry['f3_id']!r}: notes={entry['notes']!r}, "
                f"expected {F3_ONLY_NOTE!r}"
            )

    def test_f3_only_ids_are_complete_and_ordered(self, f3_only_entries):
        """The set of F3-only f3_ids must match the expected list exactly."""
        actual_ids = [e["f3_id"] for e in f3_only_entries]
        assert set(actual_ids) == set(NEW_F3_ONLY_IDS), (
            "Mismatch in F3-only f3_id set.\n"
            f"  Missing : {set(NEW_F3_ONLY_IDS) - set(actual_ids)}\n"
            f"  Extra   : {set(actual_ids) - set(NEW_F3_ONLY_IDS)}"
        )


# ---------------------------------------------------------------------------
# 7. Parametrized: each new f3_id is individually resolvable
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("f3_id", NEW_F3_ONLY_IDS)
def test_new_f3_only_entry_present(crosswalk, f3_id):
    """Every new F3-only ID from the PR diff must appear in the crosswalk."""
    matches = [e for e in crosswalk if e.get("f3_id") == f3_id]
    assert len(matches) >= 1, f"f3_id {f3_id!r} not found in crosswalk.json"


@pytest.mark.parametrize("f3_id,expected_name", list(NEW_F3_ONLY_NAMES.items()))
def test_new_f3_only_entry_name(crosswalk, f3_id, expected_name):
    """Each new entry's f3_name must match the value from the PR diff."""
    matches = [e for e in crosswalk if e.get("f3_id") == f3_id]
    assert matches, f"f3_id {f3_id!r} not found in crosswalk"
    entry = matches[0]
    assert entry["f3_name"] == expected_name, (
        f"f3_id {f3_id!r}: f3_name={entry['f3_name']!r}, expected {expected_name!r}"
    )


# ---------------------------------------------------------------------------
# 8. Boundary / regression cases
# ---------------------------------------------------------------------------

class TestBoundaryAndRegression:
    def test_first_new_entry_is_f1002(self, crosswalk):
        """F1002 (first entry added by this PR) must be present and correctly typed."""
        matches = [e for e in crosswalk if e.get("f3_id") == "F1002"]
        assert matches, "F1002 not found in crosswalk.json"
        entry = matches[0]
        assert entry["f3_name"] == "Abuse of Public-Facing API"
        assert entry["relationship"] == "unmapped"
        assert entry["confidence"] == "none"
        assert entry["ft3_id"] is None
        assert entry["ft3_name"] is None
        assert entry["notes"] == F3_ONLY_NOTE

    def test_last_new_entry_is_t1672(self, crosswalk):
        """T1672 (last entry added by this PR) must be present and correctly typed."""
        matches = [e for e in crosswalk if e.get("f3_id") == "T1672"]
        assert matches, "T1672 not found in crosswalk.json"
        entry = matches[0]
        assert entry["f3_name"] == "Email Spoofing"
        assert entry["relationship"] == "unmapped"
        assert entry["confidence"] == "none"
        assert entry["ft3_id"] is None
        assert entry["ft3_name"] is None
        assert entry["notes"] == F3_ONLY_NOTE

    def test_f3_only_entries_appear_after_derived_entries(self, crosswalk):
        """All F3-only entries added in this PR must appear after the last
        'derived' entry — they should not have been inserted mid-array."""
        last_derived_idx = max(
            (i for i, e in enumerate(crosswalk) if e["relationship"] == "derived"),
            default=-1,
        )
        first_f3_only_idx = min(
            (
                i for i, e in enumerate(crosswalk)
                if e.get("f3_id") in set(NEW_F3_ONLY_IDS)
            ),
            default=len(crosswalk),
        )
        assert first_f3_only_idx > last_derived_idx, (
            "New F3-only entries appear before 'derived' entries — unexpected ordering"
        )

    def test_sub_technique_entries_have_parent_in_new_entries(self, entries_by_f3_id):
        """Every new sub-technique (ID contains '.') must have its parent
        technique ID also present somewhere in the crosswalk."""
        sub_ids = [fid for fid in NEW_F3_ONLY_IDS if "." in fid]
        for sub_id in sub_ids:
            parent_id = sub_id.split(".")[0]
            assert parent_id in entries_by_f3_id, (
                f"Sub-technique {sub_id!r} has no parent entry for {parent_id!r}"
            )

    def test_total_entry_count_includes_new_rows(self, crosswalk):
        """Total entry count must be at least 234 (pre-PR entries + 98 new ones)."""
        assert len(crosswalk) >= 234, (
            f"Expected at least 234 entries, got {len(crosswalk)}"
        )

    def test_unmapped_count_increased_by_new_entries(self, crosswalk):
        """Number of unmapped entries must be at least as large as the count of
        new F3-only entries — a regression would indicate some were removed."""
        unmapped_count = sum(
            1 for e in crosswalk if e["relationship"] == "unmapped"
        )
        assert unmapped_count >= len(NEW_F3_ONLY_IDS), (
            f"Only {unmapped_count} unmapped entries; expected at least {len(NEW_F3_ONLY_IDS)}"
        )

    def test_pre_existing_equivalent_entries_intact(self, crosswalk):
        """Spot-check that the original 'equivalent' row for T1598 was not
        disturbed by the PR."""
        matches = [e for e in crosswalk if e.get("f3_id") == "T1598"]
        assert matches, "T1598 not found — pre-existing entry may have been removed"
        entry = matches[0]
        assert entry["relationship"] == "equivalent"
        assert entry["confidence"] == "exact"
        assert entry["ft3_id"] == "FT001"
        assert entry["ft3_name"] == "Phishing for Information"

    def test_negative_nonexistent_f3_id_absent(self, crosswalk):
        """An arbitrary ID that was never added must not appear in the file."""
        phantom_id = "F9999"
        matches = [e for e in crosswalk if e.get("f3_id") == phantom_id]
        assert not matches, f"Unexpected entry for {phantom_id!r} found"

    def test_t_prefixed_new_entries_present(self, entries_by_f3_id):
        """All T-prefixed IDs introduced by the PR must be in the crosswalk."""
        t_ids = [fid for fid in NEW_F3_ONLY_IDS if fid.startswith("T")]
        for tid in t_ids:
            assert tid in entries_by_f3_id, f"T-prefixed id {tid!r} not found"

    def test_f_prefixed_new_entries_present(self, entries_by_f3_id):
        """All F-prefixed IDs introduced by the PR must be in the crosswalk."""
        f_ids = [fid for fid in NEW_F3_ONLY_IDS if fid.startswith("F")]
        for fid in f_ids:
            assert fid in entries_by_f3_id, f"F-prefixed id {fid!r} not found"