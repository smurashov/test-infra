set timeout 160
spawn scp config.js [lindex $argv 0]@[lindex $argv 1]:~
expect "100%"
interact
set timeout 2000
spawn /usr/bin/ssh  [lindex $argv 0]@[lindex $argv 1]
expect "$ "
send "cp config.js pumphouse/tests/functional/.\r"
expect "$ "
send "git clone git://github.com/ry/node.git\r"
expect "$ "
send "cd node\r"
expect "$ "
send "sudo ./configure\r"
expect "$ "
send "sudo make\r"
expect "$ "
send "sudo make install\r"
expect "$ "
send "cd\r"
expect "$ "
send "cd pumphouse/tests/functional\r"
expect "$ "
send "npm install\r"
expect "$ "
send "node index &> ~/functests.log\r"
expect "$ "
send "exit\r"