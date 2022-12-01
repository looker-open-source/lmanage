#!/bin/bash
# find_and_replace.sh
set -x #echo on

echo "Find and replace in current directory!"
echo "File pattern to look for? (eg '*.txt')"
read filepattern
echo "Existing string?"
read existing
echo "Replacement string?"
read replacement
echo "Replacing all occurences of $existing with $replacement in files matching $filepattern"

find . -type f -name "$filepattern" -print0 | xargs -0 sed -i "s/$existing /$replacement/g"
