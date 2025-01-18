#!/bin/bash
# QuickSnatch Bash Challenge Level 4
# Network Protocol Analysis Challenge

# Protocol implementation
PROTOCOL_HEADER="4B43"  # "KC" in hex
PACKET_DATA=(
    '51 55 49 43 4B 7B'  # "QUICK{"
    '6E 33 74 77 30 72'  # "n3tw0r"
    '6B 5F 70 72 30 74'  # "k_pr0t"
    '30 63 30 6C 7D'     # "0c0l}"
)

function analyze_packet() {
    local packet="$1"
    local header="${packet:0:4}"
    
    if [[ "$header" == "$PROTOCOL_HEADER" ]]; then
        echo "Valid packet header detected"
        return 0
    fi
    return 1
}

function decode_packet() {
    local packet="$1"
    # Convert hex to ASCII
    echo "$packet" | xxd -r -p
}

function send_packet() {
    local packet="$1"
    echo "Sending packet: $packet"
    if analyze_packet "$PROTOCOL_HEADER$packet"; then
        local decoded=$(decode_packet "$packet")
        echo "Decoded content: $decoded"
    else
        echo "Invalid packet format"
    fi
}

# Main execution
echo "Network Protocol Analysis Started"
echo "--------------------------------"
echo "Protocol Header: $PROTOCOL_HEADER"
echo "Number of packets: ${#PACKET_DATA[@]}"
echo

for packet in "${PACKET_DATA[@]}"; do
    send_packet "$packet"
    sleep 1  # Simulate network delay
done
