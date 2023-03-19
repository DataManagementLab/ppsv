#!/bin/bash
# create test database

echo "Do you want to create a prefilled Database? This will delete all current Data"

select yn in "Yes" "No"; do
  case $yn in
    Yes ) echo "confirmed"; python3 ../ppsv/manage.py flush --noinput; break;;
    No ) echo "cancelled"; exit;;
  esac
done

python3 ../ppsv/manage.py runscript createTestDB
exit