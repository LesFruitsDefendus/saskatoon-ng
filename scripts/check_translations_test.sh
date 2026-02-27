#!/bin/bash

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
source "$DIR/check_translations.sh"

PASS=0
FAIL=0

# Test 1: Timestamp + line-number changes only — should NOT be meaningful
diff_non_meaningful=$(cat <<'EOF'
--- a/app/locale/fr/LC_MESSAGES/django.po
+++ b/app/locale/fr/LC_MESSAGES/django.po
-"POT-Creation-Date: 2026-01-26 20:03-0500\n"
+"POT-Creation-Date: 2026-02-23 16:04+0100\n"
-#: member/models.py:249 member/models.py:463
+#: member/models.py:246 member/models.py:460
EOF
)
if has_meaningful_changes "$diff_non_meaningful"; then
    echo "FAIL: timestamp + comments should be ignored"
    FAIL=$((FAIL + 1))
else
    PASS=$((PASS + 1))
fi

# Test 2: Actual translation change — SHOULD be meaningful
diff_real_change=$(cat <<'EOF'
--- a/app/locale/fr/LC_MESSAGES/django.po
+++ b/app/locale/fr/LC_MESSAGES/django.po
-"POT-Creation-Date: 2026-01-26 20:03-0500\n"
+"POT-Creation-Date: 2026-02-23 16:04+0100\n"
-#: member/models.py:249 member/models.py:463
+#: member/models.py:246 member/models.py:460
-msgstr "Voisinage"
+msgstr "Arrondissement"
EOF
)
if has_meaningful_changes "$diff_real_change"; then
    PASS=$((PASS + 1))
else
    echo "FAIL: actual translation change not detected"
    FAIL=$((FAIL + 1))
fi

echo ""
echo "Results: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ] || exit 1
