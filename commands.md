# QuickSnatch CTF Commands Guide

This document contains all available commands and their expected outputs for each level in the QuickSnatch CTF challenge.

## Level 1 - File Explorer

Basic file listing commands:

```bash
$ ls
Documents/  Downloads/  Pictures/  README.txt  hello.sh

$ ls -a
.  ..  .bash_history  .bashrc  .hidden_flag.txt  Documents/  Downloads/  Pictures/  README.txt  hello.sh

$ ls -l
total 28
drwxr-xr-x 2 user user 4096 Jan 18 05:55 Documents
drwxr-xr-x 2 user user 4096 Jan 18 05:55 Downloads
drwxr-xr-x 2 user user 4096 Jan 18 05:55 Pictures
-rw-r--r-- 1 user user  158 Jan 18 05:55 README.txt
-rwxr-xr-x 1 user user  237 Jan 18 05:55 hello.sh

$ ls -la
total 48
drwxr-xr-x 6 user user 4096 Jan 18 05:55 .
drwxr-xr-x 3 user user 4096 Jan 18 05:55 ..
-rw------- 1 user user    0 Jan 18 05:55 .bash_history
-rw-r--r-- 1 user user  220 Jan 18 05:55 .bashrc
-rw-r--r-- 1 user user   52 Jan 18 05:55 .hidden_flag.txt
drwxr-xr-x 2 user user 4096 Jan 18 05:55 Documents
drwxr-xr-x 2 user user 4096 Jan 18 05:55 Downloads
drwxr-xr-x 2 user user 4096 Jan 18 05:55 Pictures
-rw-r--r-- 1 user user  158 Jan 18 05:55 README.txt
-rwxr-xr-x 1 user user  237 Jan 18 05:55 hello.sh
```

Directory contents:
```bash
$ ls Documents
notes.txt  project.md

$ ls Downloads
archive.zip  data.csv

$ ls Pictures
profile.jpg  screenshot.png
```

File contents:
```bash
$ cat README.txt
Welcome to Level 1!
Try using different ls commands to find hidden files.
Hint: Some files might be hidden with a dot (.)

$ cat .hidden_flag.txt
Good job finding this hidden file!
The flag is: QUICK{b4sh_c0mp1l3r_b3g1nn3r}

$ cat hello.sh
#!/bin/bash
# QuickSnatch Bash Challenge Level 1
# Find the hidden flag!

echo "Welcome to Level 1"
echo "Can you find the hidden flag?"

# Hidden flag: QUICK{b4sh_c0mp1l3r_b3g1nn3r}

function check_flag() {
    echo "Checking for flag..."
}

check_flag
```

System information:
```bash
$ pwd
/home/user

$ whoami
user

$ id
uid=1000(user) gid=1000(user) groups=1000(user)

$ date
Sat Jan 18 05:55:53 IST 2025
```

## Level 2 - Permissions

Basic commands:
```bash
$ ls
instructions.txt  permissions_info.txt  secret.txt

$ ls -l
total 16
-rw-r--r-- 1 user user  158 Jan 18 05:55 instructions.txt
-rw-r--r-- 1 user user  237 Jan 18 05:55 permissions_info.txt
-rw------- 1 user user   21 Jan 18 05:55 secret.txt
```

File contents:
```bash
$ cat instructions.txt
Welcome to Level 2!
You need to understand file permissions to proceed.
Check permissions_info.txt for more details.

$ cat permissions_info.txt
File permissions in Linux:
r (read) = 4
w (write) = 2
x (execute) = 1

Example: chmod 644 file
6 (rw-) for owner
4 (r--) for group
4 (r--) for others

$ chmod 644 secret.txt
# (no output)

$ cat secret.txt
flag{chmod_master}
```

## Level 3 - Log Explorer

Basic commands:
```bash
$ ls
logs  system.log

$ ls logs
error.log  access.log  debug.log
```

Log contents:
```bash
$ cat logs/error.log
[ERROR] 14:30:00 - Critical system failure
[ERROR] 14:30:15 - Database connection lost
[ERROR] 14:30:30 - flag{grep_master_123} - Authentication failed
[ERROR] 14:30:45 - Memory allocation error

$ cat logs/access.log
192.168.1.100 - - [16/Jan/2025:14:30:00 +0530] "GET /admin HTTP/1.1" 403 287
192.168.1.101 - - [16/Jan/2025:14:30:15 +0530] "POST /login HTTP/1.1" 401 401
192.168.1.102 - - [16/Jan/2025:14:30:30 +0530] "GET /flag HTTP/1.1" 404 289

$ cat logs/debug.log
DEBUG: Initializing system components...
DEBUG: Loading configuration from /etc/config.json
DEBUG: Starting background services
DEBUG: flag{grep_master_123} found in memory
DEBUG: Cleanup routine started
```

Search commands:
```bash
$ grep -r flag logs
logs/error.log:[ERROR] 14:30:30 - flag{grep_master_123} - Authentication failed
logs/debug.log:DEBUG: flag{grep_master_123} found in memory
```

## Level 4 - Process Hunter

Process listing:
```bash
$ ps aux
USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root         1  0.0  0.0   2384   668 ?        Ss   14:30   0:00 /sbin/init
root       423  0.0  0.0   2880   712 ?        S    14:30   0:00 sshd
user      1234  0.0  0.1   5984  1024 pts/0    S+   14:30   0:00 suspicious_process
user      1337  0.0  0.1  10240  1024 pts/0    S+   14:30   0:00 flag_service

$ ps -p 1337
  PID TTY      STAT   TIME COMMAND
 1337 pts/0    S+     0:00 flag_service
```

Process information:
```bash
$ cat /proc/1337/cmdline
flag_service--secret--flag=flag{process_hunter}

$ strings /proc/1337/environ
SHELL=/bin/bash
PWD=/home/user
FLAG=flag{process_hunter}
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin
```

## Level 5 - Network Ninja

Network commands:
```bash
$ netstat -tuln
Active Internet connections (only servers)
Proto Recv-Q Send-Q Local Address           Foreign Address         State      
tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN     
tcp        0      0 0.0.0.0:1337            0.0.0.0:*               LISTEN

$ nc localhost 1337
Welcome! The flag is: flag{network_ninja}

$ curl localhost:1337
Welcome! The flag is: flag{network_ninja}
```

## Level 6 - Bash Wizard

File operations:
```bash
$ ls
data.txt  process.sh

$ cat data.txt
user1,100
user2,200
user3,300
admin,flag{bash_wizard}
user4,400

$ cat process.sh
#!/bin/bash
# This script processes data.txt
grep "admin" data.txt | cut -d',' -f2

$ chmod +x process.sh
# (no output)

$ ./process.sh
flag{bash_wizard}
```

## Level 7 - Archive Master

Archive handling:
```bash
$ ls -l mystery.tar.gz
-rw-r--r-- 1 user user 2048 Jan 18 05:55 mystery.tar.gz

$ tar xzf mystery.tar.gz
# (no output)

$ ls
mystery.tar.gz  secret.zip

$ unzip secret.zip
Archive:  secret.zip
  inflating: hidden.bz2

$ bzip2 -d hidden.bz2
# (no output)

$ cat hidden
flag{archive_master_explorer}
```

## Level 8 - System Monitor

System monitoring:
```bash
$ top
top - 14:30:00 up 0 min,  1 user,  load average: 0.15, 0.05, 0.01
Tasks: 105 total,   1 running, 103 sleeping,   0 stopped,   1 zombie
%Cpu(s):  5.9 us,  2.0 sy,  0.0 ni, 91.2 id,  0.0 wa,  0.0 hi,  0.9 si,  0.0 st
MiB Mem :   7950.8 total,   7450.8 free,    300.0 used,    200.0 buff/cache
MiB Swap:   2048.0 total,   2048.0 free,      0.0 used.   7450.8 avail Mem 

  PID USER      PR  NI    VIRT    RES    SHR S  %CPU  %MEM     TIME+ COMMAND
 1337 user      20   0   10240   1024    512 R  13.37  0.1   0:01.23 suspicious_svc

$ strings /proc/1337/environ
SHELL=/bin/bash
PWD=/home/user
SECRET_FLAG=flag{system_monitor_pro}
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin
```

## Level 9 - Cron Detective

Cron jobs:
```bash
$ crontab -l
* * * * * /usr/local/bin/expose_flag.sh
*/2 * * * * /usr/local/bin/cleanup_flags.sh

$ cat /usr/local/bin/expose_flag.sh
#!/bin/bash
# This script exposes the flag temporarily
echo "flag{cr0n_master_detective}" > /tmp/exposed_flag

$ cat /tmp/exposed_flag
flag{cr0n_master_detective}
```

## Level 10 - Ultimate Challenge

Network and encoding:
```bash
$ netstat -tuln
Active Internet connections (only servers)
Proto Recv-Q Send-Q Local Address           Foreign Address         State      
tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN     
tcp        0      0 0.0.0.0:31337           0.0.0.0:*               LISTEN

$ nc localhost 31337
Welcome to the Flag Service!
Here's your encrypted flag:
SGVyZSdzIHlvdXIgZmxhZzogZmxhZ3t1bHRpbWF0ZV9oYWNrZXJfcHJvfQo=

$ echo "SGVyZSdzIHlvdXIgZmxhZzogZmxhZ3t1bHRpbWF0ZV9oYWNrZXJfcHJvfQo=" | base64 -d
Here's your flag: flag{ultimate_hacker_pro}
```
