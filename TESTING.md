# QuickSnatch Platform Testing Guide

## Test Cases and Command Verification

### Level 1: Terminal Explorer
**Test Commands:**
```bash
pwd                     # Verify working directory display
ls                     # Test basic directory listing
ls -la                 # Test hidden file display
cat .hidden_flag       # Test file reading
```
**Expected Behavior:**
- Terminal shows current directory
- Lists visible files
- Shows hidden files with permissions
- Displays file contents

### Level 2: Permission Master
**Test Commands:**
```bash
ls -l                  # View file permissions
chmod 644 test.txt     # Test permission changes
chmod +x script.sh     # Test executable permissions
./script.sh            # Test script execution
```
**Expected Behavior:**
- Shows file permissions correctly
- Updates permissions as expected
- Marks files as executable
- Executes permitted scripts

### Level 3: Search and Find
**Test Commands:**
```bash
find . -name "*.txt"   # Test file search
grep "flag" *          # Test content search
locate secret          # Test system search
which python          # Test command location
```
**Expected Behavior:**
- Lists matching files
- Shows matching content
- Locates system files
- Finds command paths

### Level 4: Process Control
**Test Commands:**
```bash
ps aux               # List processes
top                  # Process monitor
kill -l              # List signals
pgrep python        # Find process IDs
```
**Expected Behavior:**
- Shows running processes
- Displays system resources
- Lists available signals
- Finds specific processes

### Level 5: Network Tools
**Test Commands:**
```bash
ifconfig             # Network interfaces
netstat -an          # Network connections
ping localhost       # Network connectivity
curl localhost:5000  # HTTP requests
```
**Expected Behavior:**
- Shows network config
- Lists open ports
- Tests connectivity
- Makes HTTP requests

### Level 6: Cryptography
**Test Commands:**
```bash
base64 -d file.txt   # Test base64 decode
xxd file.bin         # Test hex view
rot13 message.txt    # Test ROT13
md5sum file.txt      # Test hashing
```
**Expected Behavior:**
- Decodes base64 content
- Shows hex dump
- Decodes ROT13
- Generates checksums

## System Testing Checklist

### User Interface
- [ ] Terminal renders correctly
- [ ] Command history works
- [ ] Auto-completion functions
- [ ] Error messages display properly

### Level Progression
- [ ] Level completion tracked
- [ ] Flags validate correctly
- [ ] Progress saves properly
- [ ] Levels unlock sequentially

### Security Features
- [ ] Input sanitization works
- [ ] Command restrictions active
- [ ] Session handling secure
- [ ] No privilege escalation

### Performance
- [ ] Commands execute quickly
- [ ] No memory leaks
- [ ] Handles concurrent users
- [ ] Loads levels efficiently

## Test Environment Setup
```bash
# Clone testing environment
git clone https://github.com/AryanVBW/QuickSnatch.git
cd QuickSnatch

# Install dependencies
pip install -r requirements.txt

# Start test server
python app.py

# Run test suite
python -m pytest tests/
```

## Reporting Issues
1. Document the exact command
2. Note expected vs actual behavior
3. Include error messages
4. Specify test environment
5. Add reproduction steps

---
Note: This document is for testing purposes only. Keep this separate from user documentation to maintain the learning experience integrity.
