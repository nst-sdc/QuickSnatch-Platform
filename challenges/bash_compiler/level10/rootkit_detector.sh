#!/bin/bash
# QuickSnatch Bash Challenge Level 10
# Advanced Rootkit Detection Challenge

# The flag is: QUICK{r00tk1t_hunt3r_pr0}

# Function to simulate rootkit behavior
function create_rootkit_traces() {
    # Create hidden process info
    cat > /tmp/hidden_proc_$$ << EOF
Hidden Process Information
-------------------------
PID: 1337
Name: quicksnatch_rootkit
Status: Running
Hidden Files:
  - /etc/shadow.bak
  - /tmp/.hidden_flag
  - /proc/1337/root
Hidden Ports:
  - TCP 31337
  - UDP 31338

Memory Regions:
--------------
0x1000-0x2000: Code Section
0x2000-0x3000: Data Section
0x3000-0x4000: Hidden Data
  
Flag Location: 0x3337
Flag Data (encoded): $(echo "QUICK{r00tk1t_hunt3r_pr0}" | base64)
EOF
}

# Function to hide process
function hide_process() {
    # Simulate process hiding
    echo "Process hiding activated..."
    ps aux | grep -v "quicksnatch_rootkit"
}

# Function to simulate rootkit detection
function detect_rootkit() {
    echo "Starting rootkit detection..."
    create_rootkit_traces
    
    # Add some fake system calls
    echo "Intercepted system calls:"
    echo "- sys_read"
    echo "- sys_write"
    echo "- sys_getdents64"
    
    # Give hints about rootkit detection
    echo
    echo "Hint 1: Check /tmp/hidden_proc_$$ for traces"
    echo "Hint 2: The flag is base64 encoded"
    echo "Hint 3: Look for hidden processes and files"
    echo "Hint 4: Analyze memory regions at offset 0x3337"
}

# Main execution
echo "Advanced Rootkit Detection Challenge"
echo "---------------------------------"
echo "Find and analyze the rootkit to retrieve the flag!"

# Start the challenge
detect_rootkit

# Wait for analysis
sleep 30

# Cleanup
rm -f /tmp/hidden_proc_$$ 2>/dev/null
