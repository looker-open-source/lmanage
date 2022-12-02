#!/bin/bash
# find_and_replace.sh
# set -x #echo on
echo 'p for poetry run added in or np for vimspector'
read INPUT

echo "your input is $INPUT"

POETRY="p"
NOTPOETRY="np"

if [ "$POETRY" == "$INPUT" ]
then
   find . -type f -name "*.py" -print0 | xargs -0 sed -i -e 's/from configurator/from lmanage.configurator/g' -e 's/from utils/from lmanage.utils/g' -e 's/from capturator/from lmanage.capturator/g' 

else
   echo  'unpoetizing'
fi 

if [ $NOTPOETRY == $INPUT ]
then
   find . -type f -name "*.py" -print0 | xargs -0 sed -i -e 's/from lmanage.configurator/from configurator/g' -e 's/from lmanage.utils/from utils/g' -e 's/from lmanage.capturator/from capturator/g' 

else
   echo 'poetizing'
fi
