set timeout 160
spawn /usr/bin/ssh  [lindex $argv 0]@[lindex $argv 1]
expect "$ "
send "git clone https://github.com/openstack-dev/devstack\r"
expect "$ "
send "touch devstack/localrc\r"
expect "$ "
send "echo \"ADMIN_PASSWORD=111\" >> devstack/localrc\r"
expect "$ "
send "echo \"MYSQL_PASSWORD=111\" >> devstack/localrc\r"
expect "$ "
send "echo \"RABBIT_PASSWORD=111\" >> devstack/localrc\r"
expect "$ "
send "echo \"SERVICE_PASSWORD=111\" >> devstack/localrc\r"
expect "$ "
send "echo \"SERVICE_TOKEN=111\" >> devstack/localrc\r"
expect "$ "
send "cd devstack\r"
expect "$ "
set timeout 2000
send "./stack.sh\r"
expect "$ "
send "exit\r"

