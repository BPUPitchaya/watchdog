# WATCHDOG AI Dashboard - User Guide

## Quick Start (3 Easy Steps)

### Step 1: Install
**Mac/Linux:**
```bash
python3 setup.py
```

**Windows:**
```bash
python setup.py
```

### Step 2: Launch
**Mac/Linux:**
```bash
./launch_watchdog.sh
```

**Windows:**
Double-click `launch_watchdog.bat`

### Step 3: Use
1. Accept the Terms & Conditions
2. Complete the quick setup wizard
3. Start monitoring your network!

---

## What You'll See

### First Launch
1. **Splash Screen** - WATCHDOG logo appears for 5 seconds
2. **Terms & Conditions** - Read and accept to continue
3. **Setup Wizard** - Configure your preferences (first time only)
4. **Main Dashboard** - Your network monitoring control center

### Main Dashboard Features
- **Live Traffic** - Real-time network activity
- **Threat Detection** - AI-powered security alerts
- **System Tray** - Minimize to background monitoring
- **Notifications** - Security alerts on your desktop

---

## Troubleshooting

### "Permission Denied" Error
**Solution:** Run with administrator privileges
- **Mac:** Use sudo or enter password when prompted
- **Windows:** Right-click and "Run as Administrator"
- **Linux:** Use `sudo` command

### Application Won't Start
**Solution:** 
1. Make sure Python 3.8+ is installed
2. Run the setup script again: `python3 setup.py`
3. Check that all dependencies are installed

### Network Monitoring Not Working
**Solution:**
1. Verify you have administrator privileges
2. Check your network connection
3. Try restarting the application

---

## Key Features

### What It Does
- Monitors your network traffic in real-time
- Detects security threats using AI
- Blocks suspicious IP addresses
- Sends you security alerts
- Works 100% locally - no cloud sync

### Privacy Guarantee
- **All data stays on your device**
- **No data transmitted to external servers**
- **No cloud sync or remote storage**
- **Your network traffic never leaves your computer**

---

## Tips for Best Results

### For Home Users
- Run the application when you're concerned about network security
- Check the "Live Sentinel" page for real-time threats
- Use the "Autonomous Shield" to block suspicious IPs

### For Small Businesses
- Keep the application running in the background (system tray)
- Enable desktop notifications for immediate alerts
- Review the "Forensic Vault" for security incidents
- Use the "AI Mentor" for security recommendations

### For Advanced Users
- Customize alert thresholds in settings
- Adjust packet capture limits
- Configure notification preferences
- Export security reports

---

## Getting Help

### Common Issues
- **Installation problems:** Run `python3 setup.py` again
- **Permission errors:** Run as administrator
- **Network issues:** Check your connection and restart

### Support Resources
- **Quick Start Guide:** See `QUICK_START.md`
- **Technical Documentation:** See `README.md`
- **Issues:** Check the GitHub repository

---

## Customization

### Change Settings
1. Click the gear icon (Settings)
2. Adjust your preferences
3. Click "Save"

### Notification Preferences
1. Go to Settings
2. Select "Notifications"
3. Choose which alerts you want
4. Click "Save"

### Theme Options
1. Go to Settings
2. Select "Appearance"
3. Choose your preferred theme
4. Click "Save"

---

## Security Best Practices

### Recommended Settings
- Enable desktop notifications
- Keep system tray icon active
- Set alert threshold to medium
- Enable automatic IP blocking
- Review security incidents weekly

### What to Monitor
- Unusual network activity
- Connections from unknown IPs
- High traffic volumes
- Repeated connection attempts

---

## Understanding the Dashboard

### Live Sentinel
- Real-time network traffic
- Current threat level
- Active connections
- Packet capture statistics

### Autonomous Shield
- Blocked IP addresses
- Firewall status
- Manual IP blocking
- Block history
- **Clear All Blocked IPs**: Bulk removal of all blocked IPs
  - Navigate to Settings → Security tab
  - Click "Clear All Blocked IPs" button (red styling)
  - Requires double confirmation to prevent accidental clearing
  - Removes all IPs from the pf table and cancels timers

### Forensic Vault
- Security incidents
- Threat details
- Packet analysis
- Incident timeline

### AI Mentor
- Security recommendations
- Threat explanations
- Best practices
- System health
- **Analyze Last Threat**: Get AI analysis of the most recent detected threat
  - Click "Analyze Last Threat" in Quick Actions
  - AI provides SME-friendly explanations
  - Includes business impact and mitigation steps
  - Shows "AI is thinking..." while processing
- **Test Threat**: Create mock threats for testing
  - Click "Test Threat" in Quick Actions
  - Creates a sample DDoS attack scenario
  - Useful for testing when no real threats are detected

---

## Status Indicators

### Green (Safe)
- No threats detected
- Normal network activity
- All systems operational

### Yellow (Caution)
- Suspicious activity detected
- Elevated threat level
- Monitor closely

### Red (Danger)
- Active threat detected
- Immediate action required
- Security breach possible

---

## Data Management

### Automatic Cleanup
- Old data is automatically deleted based on retention settings
- Default: 30 days
- Can be customized in settings

### Manual Cleanup
1. Go to Settings
2. Select "Data Management"
3. Choose cleanup options
4. Click "Clean Now"

### Export Data
1. Go to Forensic Vault
2. Click "Export"
3. Choose format (CSV, JSON)
4. Save to your computer

---

## Learning Resources

### For Beginners
- Start with the "Live Sentinel" page
- Read the tooltips on each section
- Check the "AI Mentor" for explanations

### For Intermediate Users
- Explore the "Autonomous Shield" features
- Customize your alert settings
- Review the "Forensic Vault" regularly

### For Advanced Users
- Adjust ML model parameters
- Configure custom firewall rules
- Export and analyze packet data

---

## Updates & Maintenance

### Automatic Updates
- The application checks for updates automatically
- You'll be notified when updates are available
- Updates are installed with one click

### Manual Updates
1. Check the GitHub repository
2. Download the latest version
3. Run the setup script
4. Your settings will be preserved

---

## System Requirements

### Minimum Requirements
- **OS:** macOS 10.14+, Windows 10+, or Linux
- **RAM:** 4GB (8GB recommended)
- **Storage:** 500MB free space
- **Network:** Active internet connection
- **Python:** 3.8 or higher (for manual installation)

### Recommended Requirements
- **OS:** macOS 12+, Windows 11+, or modern Linux
- **RAM:** 8GB or more
- **Storage:** 1GB free space
- **Network:** High-speed internet
- **Python:** 3.10 or higher

---

## You're All Set!

Your WATCHDOG AI Dashboard is now protecting your network. 

**Remember:**
- Keep it running in the background for continuous protection
- Check notifications regularly
- Review security incidents weekly
- Keep the application updated

**Need Help?** Check the documentation or visit the GitHub repository.

---

**Version:** 2.0  
**Last Updated:** 2024  
**Privacy:** 100% Local - No Cloud Sync
