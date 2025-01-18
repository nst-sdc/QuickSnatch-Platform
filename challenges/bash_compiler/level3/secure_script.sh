#!/bin/bash
# QuickSnatch Bash Challenge Level 3
# Anti-Debug Challenge

# Anti-debugging check with bypass hint
if [ -n "$(ps -p $$ -o cmd= | grep -E 'strace|ltrace|gdb')" ]; then
    echo "Nice try! But debugging isn't allowed!"
    echo "Hint: Try analyzing the binary statically first"
    exit 1
fi

# Time-based execution check (more forgiving)
TIMESTAMP=$(date +%s)
if [ $((TIMESTAMP % 2)) -ne 0 ]; then
    echo "Timing is everything! Try again in 1 second..."
    echo "Hint: The check passes on even seconds"
    exit 1
fi

# Flag components with hints
FLAG_PART1="QUICK{"
FLAG_PART2="4nt1_"
FLAG_PART3="d3bug_"
FLAG_PART4="m4st3r}"

# Multi-layer encryption
function encrypt_flag() {
    local input="$1"
    local key="$2"
    echo "$input" | openssl enc -aes-128-cbc -a -salt -pass pass:"$key" 2>/dev/null
}

# Decryption function with error handling
function decrypt_flag() {
    local input="$1"
    local key="$2"
    local result
    result=$(echo "$input" | openssl enc -aes-128-cbc -a -d -salt -pass pass:"$key" 2>/dev/null)
    if [ $? -eq 0 ]; then
        echo "$result"
    else
        echo "Decryption failed. Try another key!"
    fi
}

# Main challenge logic
echo "Level 3 - Anti-Debug Challenge"
echo "-----------------------------"
echo "Hint 1: Flag parts are encrypted with different keys"
echo "Hint 2: Keys are based on process information"
echo "Hint 3: Check /proc/self for useful information"

# Store encrypted flag parts
ENCRYPTED_PART1=$(encrypt_flag "$FLAG_PART1" "pid_$$")
ENCRYPTED_PART2=$(encrypt_flag "$FLAG_PART2" "ppid_$PPID")
ENCRYPTED_PART3=$(encrypt_flag "$FLAG_PART3" "uid_$UID")
ENCRYPTED_PART4=$(encrypt_flag "$FLAG_PART4" "time_$TIMESTAMP")

# Output encrypted parts with hints
echo
echo "Encrypted flag parts:"
echo "Part 1: $ENCRYPTED_PART1 (Key hint: Current process)"
echo "Part 2: $ENCRYPTED_PART2 (Key hint: Parent process)"
echo "Part 3: $ENCRYPTED_PART3 (Key hint: User identity)"
echo "Part 4: $ENCRYPTED_PART4 (Key hint: Current time)"
