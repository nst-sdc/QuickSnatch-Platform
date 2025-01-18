#!/bin/bash
# QuickSnatch Bash Challenge Level 1
# Find the hidden flag!

echo 'Welcome to Level 1'
echo 'Can you find the hidden flag?'

# Hidden flag: QUICK{b4sh_c0mp1l3r_b3g1nn3r}
# The flag above is commented out and will be visible in the binary

function check_flag() {
    # This function contains the flag but it's hidden
    local flag="QUICK{b4sh_c0mp1l3r_b3g1nn3r}"
    echo "Checking for flag..."
}

# The flag is also encoded in this variable
FLAG_DATA="51 55 49 43 4B 7B 62 34 73 68 5F 63 30 6D 70 31 6C 33 72 5F 62 33 67 31 6E 6E 33 72 7D"

# Main execution
check_flag

# Note: After compilation with shc, use strings/hexdump to find the flag
