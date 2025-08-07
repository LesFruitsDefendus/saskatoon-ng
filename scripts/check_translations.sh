#!/bin/bash

# This script checks if translation files are up to date.
# Note 1 insertion(+), 1 deletion(-) is expected on each file (creation datetime).

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# Update translation files
cd $DIR/../saskatoon
django-admin makemessages --locale fr --domain django

ret=0
for app in harvest member sitebase
do
    filename="$app/locale/fr/LC_MESSAGES/django.po"
    diffs=$(git diff --shortstat $filename | sed -E 's/.* ([0-9]+) insertion.* ([0-9]+) deletion.*/\1,\2/')
    if [ "$diffs" != "1,1" ]; then
        more=$(git diff $filename)
        echo "$filename is not up to date: $more"
        ret=1
    fi
done

exit $ret
