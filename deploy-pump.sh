set timeout 160
spawn scp result.yaml [lindex $argv 0]@[lindex $argv 1]:~
expect "100%"
interact
set timeout 500
spawn /usr/bin/ssh  [lindex $argv 0]@[lindex $argv 1]
expect "$ "
send "git clone https://github.com/MirantisLabs/pumphouse\r"
expect "$ "
send "cd pumphouse\r"
expect "$ "
send "sudo pip install --allow-external mysql-connector-python .\r"
expect "$ "
send "cd ..\r"
expect "$ "
send "screen -dmS \"pumphouse\"\r"
expect "$ "
send "screen -S \"pumphouse\" -p 0 -X stuff \"pumphouse-api result.yaml\$(printf \\\\r)\"\r"
expect "$ "
send "exit\r"
