#!/bin/bash

 

echo "Connecting to Looker API (https://rakutenadvertisingdev.cloud.looker.com:443/api/3.1)..."

curlout=$(curl -s \

               -d "client_id=j8*********Rb8&client_secret=xz************pw" \

               https://rakutenadvertisingdev.cloud.looker.com:443/api/3.1/login)

 

access_token=$(echo $curlout | jq -r '.access_token')

 

if [[ $access_token != "null" ]]; then

   echo "access_token: $access_token"

else

   echo "Error: unable to get access token"

   exit 1

fi

 

curlout=$(curl -s \

               -H "Authorization: token $access_token" \

               https://rakutenadvertisingdev.cloud.looker.com:443/api/3.1/folders/1/children)

 

indent_level=0

IterateFolder() {

 

   local folder_id=${1}

   local folder_name=${2}

   local folder_json=${3}

   printf "%*s(%d): %s\n" $((${indent_level}*5)) '' ${folder_id} "${folder_name}"

   if [[ ${folder_json} != "[]" ]]; then

      #-- Child folders exist

      indent_level=$((indent_level+1))

 

      local nbr_child_folders=$(echo ${folder_json} | jq 'length')

 

      local child_folder_index

      for (( child_folder_index=0; child_folder_index<$nbr_child_folders; child_folder_index++ )); do

         local child_folder_id=$(echo ${folder_json} | jq -r '.['${child_folder_index}'] | .id')

         local child_folder_name=$(echo ${folder_json} | jq -r '.['${child_folder_index}'] | .name')

 

         local child_folder_json=$(curl -s \

            -H "Authorization: token $access_token" \

            https://rautenadvertisingdev.cloud.looker.com:443/api/3.1/folders/${child_folder_id}/children)

 

         IterateFolder "${child_folder_id}" "${child_folder_name}" "${child_folder_json}"

      done

      indent_level=$((indent_level-1))

   fi

 

}

 

#-- Start at the root of Shared folder

echo "Looker Folders:"

IterateFolder "1" "Shared" "${curlout}"k
