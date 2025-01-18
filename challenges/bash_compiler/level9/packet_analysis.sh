#!/bin/bash
# QuickSnatch Bash Challenge Level 9
# Network Packet Analysis Challenge

# The flag is: QUICK{p4ck3t_c4ptur3_pr0}

# Function to create a fake packet capture
function create_packet_capture() {
    # Create a fake pcap-like format
    cat > /tmp/capture_$$.txt << EOF
Packet Capture Data
------------------

Packet 1:
---------
Source IP: 192.168.1.100
Dest IP: 192.168.1.200
Protocol: TCP
Payload: 51 55 49 43 4B (QUICK)

Packet 2:
---------
Source IP: 192.168.1.200
Dest IP: 192.168.1.100
Protocol: TCP
Payload: 7B 70 34 63 6B (p4ck)

Packet 3:
---------
Source IP: 192.168.1.100
Dest IP: 192.168.1.200
Protocol: TCP
Payload: 33 74 5F 63 34 (3t_c4)

Packet 4:
---------
Source IP: 192.168.1.200
Dest IP: 192.168.1.100
Protocol: TCP
Payload: 70 74 75 72 33 (ptur3)

Packet 5:
---------
Source IP: 192.168.1.100
Dest IP: 192.168.1.200
Protocol: TCP
Payload: 5F 70 72 30 7D (_pr0})

Analysis Hints:
--------------
1. Each packet contains part of the flag
2. Payload is in hex format
3. Follow TCP stream to reconstruct
4. Watch for packet ordering
EOF
}

# Function to simulate packet capture
function capture_packets() {
    echo "Starting packet capture simulation..."
    create_packet_capture
    
    # Print some analysis hints
    echo "Packet capture saved to /tmp/capture_$$.txt"
    echo
    echo "Hint 1: Use TCP stream reassembly"
    echo "Hint 2: Convert hex to ASCII"
    echo "Hint 3: Check all packet payloads"
}

# Main execution
echo "Network Packet Analysis Challenge"
echo "-------------------------------"
echo "Analyze the packet capture to find the flag!"

# Start the challenge
capture_packets

# Wait for analysis
sleep 30

# Cleanup
rm -f /tmp/capture_$$.txt 2>/dev/null
