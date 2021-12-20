#!/bin/bash
mysqldump --add-drop-table -h db -u root -ppcl123456 operatepathology > "/app/backup_mysql/operatepathology_$(date '+%Y-%m-%d %H:%M').sql"