#!/bin/bash

MYSQL_USER="root"
MYSQL_PASSWORD="root"
PRODUCTION_DB="event_bookings"
TESTING_DB="test_event_bookings"
DDL_FILE="database_setup/DDL.sql"
DML_FILE="database_setup/DML.sql"

# Function to execute a command and handle errors
execute_command() {
    command=$1
    if ! eval "$command"; then
        echo "Error executing: $command"
        exit 1
    fi
}

# Drop and recreate production database
execute_command "mysql -u $MYSQL_USER -p$MYSQL_PASSWORD -e 'DROP DATABASE IF EXISTS $PRODUCTION_DB;'"
execute_command "mysql -u $MYSQL_USER -p$MYSQL_PASSWORD -e 'CREATE DATABASE $PRODUCTION_DB;'"

# Load DDL and DML into production database
execute_command "mysql -u $MYSQL_USER -p$MYSQL_PASSWORD $PRODUCTION_DB < $DDL_FILE"
execute_command "mysql -u $MYSQL_USER -p$MYSQL_PASSWORD $PRODUCTION_DB < $DML_FILE"

# Drop and recreate testing database
execute_command "mysql -u $MYSQL_USER -p$MYSQL_PASSWORD -e 'DROP DATABASE IF EXISTS $TESTING_DB;'"
execute_command "mysql -u $MYSQL_USER -p$MYSQL_PASSWORD -e 'CREATE DATABASE $TESTING_DB;'"

# Load DDL into testing database
execute_command "mysql -u $MYSQL_USER -p$MYSQL_PASSWORD $TESTING_DB < $DDL_FILE"

echo "Databases reset and loaded successfully!"
