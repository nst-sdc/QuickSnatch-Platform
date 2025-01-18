#!/bin/bash
# QuickSnatch Bash Challenge Level 5
# Syscall Analysis Challenge

# The flag is: QUICK{5yscall_1nt3rc3pt}

function encode_flag() {
    local flag="$1"
    local encoded=""
    for ((i=0; i<${#flag}; i++)); do
        # Use write syscall to output each character
        printf "\x$(printf "%x" "'${flag:$i:1}")"
    done
}

function make_syscalls() {
    # Series of syscalls that reveal the flag
    local temp_file="/tmp/syscall_trace_$$.txt"
    
    # Create file (open syscall)
    touch "$temp_file"
    
    # Write flag data (write syscall)
    encode_flag "QUICK{5yscall_1nt3rc3pt}" > "$temp_file"
    
    # Read data back (read syscall)
    local data
    read -r data < "$temp_file"
    
    # Cleanup (unlink syscall)
    rm -f "$temp_file"
}

# Alternative method without strace
function analyze_self() {
    # Self-analysis function that doesn't require strace
    echo "Analyzing process behavior..."
    
    # Print process info that contains hints
    echo "Process ID: $$"
    echo "Parent Process: $PPID"
    
    # Show file descriptors (reveals syscall patterns)
    ls -l /proc/$$/fd 2>/dev/null
    
    # Show memory maps (reveals syscall patterns)
    head -n 5 /proc/$$/maps 2>/dev/null
}

# Main execution
echo "Syscall Analysis Challenge"
echo "-------------------------"

if [ -n "$(which strace)" ]; then
    echo "Note: Traditional syscall tracing detected"
    echo "Try alternative analysis methods..."
    analyze_self
else
    echo "Standard analysis mode"
    make_syscalls
fi

# Hidden flag components in memory maps
# Flag can be found by:
# 1. Analyzing file operations
# 2. Monitoring process memory
# 3. Checking file descriptor operations
# 4. Following syscall patterns
