#!/bin/sh
# Setup Python virtual environment, dependencies, and MariaDB server

# Some global variables
venv="CaptionBlockerVenv"
reqs="requirements.txt"
user="root"
pass="pass"
db="caption_capper"
dbg_page="about:debugging#/runtime/this-firefox"

# Colors
BLANK='\033[0m'
GREEN='\033[0;32m'
RED='\033[0;31m'

# Set color, print text, the reset color
echo_col() {
	[ "$#" -ne 2 ] && echo "echo_col: Requires 2 arguments." && exit 1
	col="$1"
	text="$2"
	echo -ne "$col"
	echo "$text"
	echo -ne "$BLANK"
}

# Print bar of this shape to stdout: <====>
bar() {
	COLS=$(tput cols)
	echo -n "<"
	for _ in $(seq "$((COLS - 2))"); do
		echo -n "="
	done
	echo -n ">"
}

# Check if binary is installed on system
isInstalled() {
	binary="$1"
	[ -n "$binary" ] || exit 1
	which "$binary" > /dev/null 2>&1 || { echo_col  "$RED" "Needed package: $binary" && exit 1; }
}

# # Check if these are installed
echo "Checking if required binaries are on system..."
isInstalled firefox
isInstalled mariadb
isInstalled pip
isInstalled python
echo_col "$GREEN" "Required binaries are on system!"
bar

# # Create Python virtual environment, then source
echo "Creating Python virtual environment..."
python -m venv "$venv"
source "$venv"/bin/activate
echo_col  "$GREEN" "Python virtual environment created!"
bar

# # Install all requirements
echo "Pip installing Python packages..."
pip install -r "$reqs"
echo_col  "$GREEN" "Python packages pip installed!"
bar

# # Check if MariaDB is running
echo "Checking if MariaDB is running..."
while true; do
	mdb_status=$(mariadb --user="$user" --password="$pass" < status.sql > /dev/null 2>&1)
	[ "$?" -eq 0 ] && break || systemctl start mariadb
done
echo_col  "$GREEN" "MariaDB is running!"
bar

# # Create MariaDB database, if it doesn't exist
create_db() {
	echo "Creating database..."
	mariadb --user="$user" --password="$pass" < create_db.sql
	mariadb --user="$user" --password="$pass" < create_table.sql
	echo_col "$GREEN" "Database created!"
}
echo "Checking if database exists..."
mariadb --user="$user" --password="$pass" < script.sql | grep -q "$db" && echo_col  "$GREEN" "Database already exists!" || create_db
bar

# Open Firefox debugging page
echo "Opening extension debugging page..."
firefox "$dbg_page"
echo_col "$GREEN" "Extension debugging page opened!"
bar
