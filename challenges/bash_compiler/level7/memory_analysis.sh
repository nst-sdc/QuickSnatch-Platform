#!/bin/bash
# QuickSnatch Bash Challenge Level 7
# Memory Analysis Challenge

# The flag is: QUICK{m3m0ry_m4pp1ng_pr0}

# Function to create memory patterns
function create_memory_pattern() {
    # Allocate some memory with dd
    dd if=/dev/zero of=/tmp/memory_map_$$ bs=1M count=1 2>/dev/null
    
    # Write flag in different memory locations
    echo "QUICK{m3m0ry_m4pp1ng_pr0}" | dd of=/tmp/memory_map_$$ bs=1 seek=500 conv=notrunc 2>/dev/null
    echo "This is a fake flag" | dd of=/tmp/memory_map_$$ bs=1 seek=100 conv=notrunc 2>/dev/null
    echo "Try harder!" | dd of=/tmp/memory_map_$$ bs=1 seek=300 conv=notrunc 2>/dev/null
}

# Function to map memory
function map_memory() {
    # Create memory mappings
    echo "Creating memory mappings..."
    create_memory_pattern
    
    # Map the file into memory
    tail -f /tmp/memory_map_$$ >/dev/null &
    TAIL_PID=$!
    
    # Give hint about memory layout
    echo "Process $TAIL_PID is mapping the flag in memory"
    echo "Hint: Check /proc/$TAIL_PID/maps and mem"
}

# Main execution
echo "Memory Analysis Challenge"
echo "-----------------------"
echo "Find the flag in process memory!"
echo "Hint 1: The flag is mapped at offset 500"
echo "Hint 2: Use memory mapping analysis"

# Start the challenge
map_memory

# Wait for analysis
sleep 30

# Cleanup
kill $TAIL_PID 2>/dev/null
rm -f /tmp/memory_map_$$ 2>/dev/null
