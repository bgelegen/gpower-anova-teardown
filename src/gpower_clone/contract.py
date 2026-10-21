"""The single place where CLI flags, mode spellings and output field names live
(CONTRACT.md section 5)."""

TEST_NAME = "anova-oneway"
# Accepted spellings of --test (compared case-insensitively, "_" == "-").
TEST_ALIASES = ["anova-oneway", "anova-one-way", "oneway-anova", "one-way-anova", "anova1", "anova"]
DEFAULT_DIGITS = 4

# Canonical mode -> accepted spellings.
MODE_ALIASES = {
    "a-priori": ["a-priori", "apriori", "a_priori"],
    "post-hoc": ["post-hoc", "posthoc", "post_hoc"],
}
APRIORI, POSTHOC = list(MODE_ALIASES)

# Canonical parameter name -> accepted flags ('_' and '-' are interchangeable;
# the first entry is the preferred spelling used in messages).
FLAG_ALIASES = {
    "test": ["--test"],
    "mode": ["--mode"],
    "f": ["--f", "--effect-size", "--es"],
    "alpha": ["--alpha"],
    "power": ["--power"],
    "groups": ["--groups", "--k", "--k-groups", "--n-groups", "--num-groups"],
    "total_n": ["--n-total", "--n", "--N", "--total-n", "--sample-size"],
    "digits": ["--digits"],
}

# Engine result attribute -> public output field, in output order.
OUTPUT_FIELDS = {
    "per_group": "n_per_group",
    "total_n": "n_total",
    "power": "actual_power",
    "critical": "critical",
    "df1": "df1",
    "df2": "df2",
    "ncp": "ncp",
}
# Output fields that are written as integers (the rest are rounded to digits).
INTEGER_FIELDS = ("total_n", "df1", "df2")

# Parameters each mode needs / tolerates (CONTRACT.md section 3).
MODE_PARAMS = {
    APRIORI: {"required": ["f", "alpha", "power", "groups"], "optional": ["digits"]},
    POSTHOC: {"required": ["f", "alpha", "total_n", "groups"], "optional": ["digits"]},
}
