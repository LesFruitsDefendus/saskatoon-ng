#!/bin/bash

# This script checks if translation files are up to date.
# Note at least 1 insertion(+), 1 deletion(-) is expected on each file (creation datetime).

# Returns 0 if diff contains only non-meaningful changes (comments, timestamps),
# returns 1 if diff contains actual translation changes.
has_meaningful_changes() {
    local diffs="$1"
    local lines meaningful
    lines=$(echo "$diffs" | grep -E '^\+|^-' | grep -v '^---' | grep -v '^+++')
    meaningful=$(echo "$lines" | grep -v '^[-+]\s*#:' | grep -v 'POT-Creation-Date:' || true)
    [ -n "$meaningful" ]
}

# Only run the main logic when executed directly, not when sourced
if [ "${BASH_SOURCE[0]}" = "$0" ]; then
    DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

    # Update translation files
    cd "$DIR/../saskatoon"
    django-admin makemessages --locale fr --domain django

    ret=0
    for app in harvest member sitebase
    do
        filename="$app/locale/fr/LC_MESSAGES/django.po"
        diffs=$(git diff --unified=0 "$filename")
        if has_meaningful_changes "$diffs"; then
            echo "$filename is not up to date:"
            echo "$diffs"
            ret=1
        fi
    done

    exit $ret
fi
