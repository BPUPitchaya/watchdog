"""Help content for all dashboard pages.

This module contains beginner-friendly explanations for every section
of the Watchdog dashboard. Each page has clickable hotspots with
detailed guidance written in simple terms.
"""

from src.ui.widgets.help_dialog import HelpHotspot

# Help content for each page - defines hotspots with beginner-friendly explanations
PAGE_HELP_CONTENT = {
    "Live Sentinel": [
        HelpHotspot(
            15,
            12,
            "System Health Gauge",
            "Think of this like a fitness tracker for your computer. It shows three key things:\n\n"
            "• CPU Usage (processor work)\n"
            "• Memory/RAM (active programs)\n"
            "• Network Activity (internet data)\n\n"
            "COLOR CODES:\n"
            "Green (0-60%) = Healthy - your computer is handling things well\n"
            " Yellow (60-80%) = Busy - some programs are working hard\n"
            " Red (80%+) = Critical - check Task Manager to see what's using resources\n\n"
            " TIP: If you see red often, you might need more RAM or fewer programs running.",
        ),
        HelpHotspot(
            40,
            12,
            "Live Traffic Monitor",
            "This is like a heart monitor but for your internet connection. It shows data flowing in real-time:\n\n"
            "WHAT IT SHOWS:\n"
            "• Blue bars = Data coming IN (downloads, web pages, emails)\n"
            "• Green bars = Data going OUT (uploads, messages sent)\n"
            "• Height = Amount of data (taller = more traffic)\n\n"
            "HOW TO READ IT:\n"
            "• Small bars = Normal browsing\n"
            "• Medium bars = Streaming video\n"
            "• Big spikes = Large downloads or potential attacks\n\n"
            "WATCH FOR: Sudden huge spikes when you're not doing anything - that could be suspicious!",
        ),
        HelpHotspot(
            85,
            12,
            "Risk Analysis Gauge",
            "This gauge shows how dangerous your current network activity looks to the AI.\n\n"
            "HOW IT WORKS:\n"
            "The AI analyzes all traffic patterns and assigns a risk score based on:\n"
            "• Known attack signatures\n"
            "• Unusual connection patterns\n"
            "• Suspicious IP addresses\n\n"
            "RISK LEVELS:\n"
            " Green (Low 0-30%) = Safe surfing - nothing suspicious detected\n"
            " Yellow (Medium 30-60%) = Caution - some unusual patterns, keep watching\n"
            " Red (High 60%+) = Danger - Likely attack detected, check Forensic Vault\n\n"
            " ACTION: If you see red, click 'View Details' or ask the AI Assistant about it.",
        ),
        HelpHotspot(
            15,
            50,
            "Network Traffic Table",
            "This is your security log showing every single network connection. Like a CCTV recording of your internet.\n\n"
            "COLUMNS EXPLAINED:\n"
            "• Source IP = Where data came from (like a return address)\n"
            "• Destination IP = Where it's going (like a mailing address)\n"
            "• Protocol = Type of 'road' data travels on\n"
            "  - TCP = Reliable (websites, emails)\n"
            "  - UDP = Fast (video calls, gaming)\n"
            "  - PROTO-1 = Unknown/Unidentified protocol\n"
            "• Length = Size of data packet (bytes)\n"
            "• Confidence Score = AI's certainty about threat level (0-100%)\n"
            "• Action = What Watchdog did (Allow/Block/Flag)\n\n"
            "ABOUT PROTO-1:\n"
            "PROTO-1 appears when Scapy can't identify the specific protocol type. This could be:\n"
            "• Encrypted traffic (HTTPS, VPN)\n"
            "• Custom protocols (special applications)\n"
            "• Network scanning tools\n"
            "• Malware using unusual communication\n\n"
            "PRO TIP: Click any row to see detailed AI analysis of that connection!",
        ),
        HelpHotspot(
            75,
            50,
            "AI Security Assistant",
            "Your personal cybersecurity expert! This chatbot helps you understand threats in plain English.\n\n"
            "WHAT YOU CAN ASK:\n"
            "• 'What does [specific IP] mean?'\n"
            "• 'Is this connection dangerous?' (paste from table)\n"
            "• 'What is a DDoS attack?'\n"
            "• 'How do I protect my network?'\n"
            "• 'Explain this threat simply'\n\n"
            "HOW TO USE:\n"
            "1. Type your question in the box below\n"
            "2. Press Enter or click Send\n"
            "3. AI responds with beginner-friendly explanations\n\n"
            "SMART FEATURE: The AI remembers your conversation, so you can ask follow-up questions!",
        ),
    ],
    "Forensic Vault": [
        HelpHotspot(
            40,
            15,
            "Flagged Incidents Table",
            "This is your security 'black box' - a complete history of every suspicious event. Think of it like a flight recorder for your network.\n\n"
            "WHAT GETS LOGGED HERE:\n"
            "• Blocked attacks (firewall stopped them)\n"
            "• Suspicious connections (flagged for review)\n"
            "• High-risk traffic (AI wasn't sure, logged it)\n"
            "• Malware attempts (viruses, trojans, etc.)\n\n"
            "HOW TO USE:\n"
            "1. Browse the list - newest threats appear at top\n"
            "2. Use the search box to find specific IPs or dates\n"
            "3. Click any row to see detailed analysis\n"
            "4. Export data if you need to report to IT/security team\n\n"
            "WHY THIS MATTERS: Even 'blocked' attacks are recorded so you can see WHO tried to attack you and WHEN.",
        ),
        HelpHotspot(
            15,
            50,
            "Threat Details Panel",
            "When you click an incident in the table, this area shows the full 'detective report' on that threat.\n\n"
            "WHAT YOU'LL SEE:\n"
            "• Attack Type: The 'weapon' used (Malware, Phishing, DDoS, etc.)\n"
            "• Confidence Score: How sure the AI is (0-100%)\n"
            "• Timestamp: Exact date and time of the incident\n"
            "• Source IP: Attacker's location on the internet\n"
            "• Target: What they tried to attack on your network\n"
            "• AI Analysis: Beginner-friendly explanation of what happened\n\n"
            "SMART FEATURE: Click 'Ask AI' to get more details about any specific incident!",
        ),
    ],
    "Autonomous Shield": [
        HelpHotspot(
            30,
            15,
            "Firewall Status",
            "This is your digital security guard - the first line of defense against hackers.\n\n"
            "WHAT IT DOES:\n"
            "The firewall acts like a bouncer at a club. It checks every connection request and:\n"
            "• Allows safe, expected traffic (your web browsing)\n"
            "• Blocks unauthorized attempts to enter your network\n"
            "• Stops known attack patterns automatically\n\n"
            "STATUS INDICATORS:\n"
            "ON (Green) = Protected - firewall is actively blocking threats\n"
            "OFF (Red) = Vulnerable - your network is exposed to attacks\n\n"
            "IMPORTANT: Only turn OFF if you're troubleshooting network issues. Always keep it ON otherwise!",
        ),
        HelpHotspot(
            70,
            15,
            "AI Protection Mode",
            "This setting controls how cautious vs. aggressive the AI is when deciding to block something.\n\n"
            "THE THREE MODES:\n\n"
            "CONSERVATIVE (Recommended for beginners)\n"
            "• Only blocks CLEAR threats\n"
            "• Very low chance of blocking good traffic\n"
            "• Might let some suspicious stuff through\n\n"
            "BALANCED (Default setting)\n"
            "• Blocks most threats\n"
            "• Occasionally might flag normal traffic\n"
            "• Good for everyday users\n\n"
            "AGGRESSIVE (For high-security needs)\n"
            "• Blocks ANYTHING slightly suspicious\n"
            "• Might block some legitimate websites/apps\n"
            "• Best for businesses or if you're under attack\n\n"
            "TIP: Start with Conservative and only increase if you get attacked frequently.",
        ),
        HelpHotspot(
            40,
            50,
            "Blocked IPs List",
            "Your 'most wanted' list of attackers! These IP addresses have been caught trying to harm your network.\n\n"
            "WHAT YOU SEE:\n"
            "• IP Address = The attacker's internet location\n"
            "• Location = Country/region (if detectable)\n"
            "• First Seen = When they started attacking you\n"
            "• Block Count = How many times they tried\n"
            "• Status = Currently blocked or unblocked\n\n"
            "WHAT YOU CAN DO:\n"
            "• View details - See what attacks they tried\n"
            "• Keep blocked - They stay banned forever\n"
            "• Unblock - Use if you blocked something by mistake\n"
            "• Report - Send to authorities for serious attackers\n\n"
            "SECURITY TIP: Never unblock IPs you don't recognize!",
        ),
    ],
    "AI Mentor": [
        HelpHotspot(
            20,
            15,
            "Chat History Panel",
            "This is your conversation log with the AI cybersecurity tutor. Everything you ask and every answer is saved here.\n\n"
            "HOW IT WORKS:\n"
            "• Your questions appear on the right\n"
            "• AI answers appear on the left\n"
            "• Scroll up to see older conversations\n"
            "• Newest messages at the bottom\n\n"
            "USEFUL FEATURES:\n"
            "• Click 'Clear Chat' to start a fresh conversation\n"
            "• AI remembers context - you can ask follow-ups\n"
            "• Copy useful answers to save them elsewhere\n\n"
            "LEARNING TIP: Ask the AI to explain the same thing multiple ways until you understand it!",
        ),
        HelpHotspot(
            60,
            15,
            "AI Model Selector",
            "Choose which 'brain' powers your AI assistant. Different models = different capabilities.\n\n"
            "MODEL OPTIONS (based on your computer's RAM):\n\n"
            "1b Model (8GB RAM)\n"
            "• Super fast responses (1-2 seconds)\n"
            "• Basic, simple answers\n"
            "• Good for quick questions\n\n"
            "3b Model (8GB+ RAM) RECOMMENDED\n"
            "• Balanced speed and quality\n"
            "• Detailed but understandable answers\n"
            "• Best for most users\n\n"
            "8b Model (16GB+ RAM)\n"
            "• Slower (5-10 seconds)\n"
            "• Very detailed, technical answers\n"
            "• Good for advanced users\n\n"
            "Phi4 Model (16GB+ RAM)\n"
            "• Best quality answers\n"
            "• Professional-grade analysis\n"
            "• Slowest but most accurate\n\n"
            "HOW TO CHECK RAM: Mac = Apple menu → About This Mac | Windows = Settings → System → About",
        ),
        HelpHotspot(
            40,
            70,
            "Question Input Box",
            "Your direct line to the AI expert! Type any cybersecurity question here and get instant help.\n\n"
            "WHAT TO ASK:\n"
            "• 'Explain [threat name] like I'm 5'\n"
            "• 'Is [IP address] dangerous?'\n"
            "• 'What should I do about [attack type]?'\n"
            "• 'How to protect against [threat]?'\n"
            "• 'What does [technical term] mean?'\n\n"
            "HOW TO ASK:\n"
            "1. Be specific - mention IP addresses from the table\n"
            "2. Ask follow-ups - 'Tell me more' or 'Explain differently'\n"
            "3. Request examples - 'Give me an example'\n\n"
            "POWER USER TIP: Paste threat details from the Traffic Table for instant analysis!",
        ),
    ],
    "Network Topology": [
        HelpHotspot(
            50,
            20,
            "Network Visualization Map",
            "A visual map of your entire home or office network - like a family tree for your devices!\n\n"
            "HOW TO READ THE MAP:\n"
            "• YOUR COMPUTER = The central hub (you are here!)\n"
            "• Lines = Network cables or WiFi connections\n"
            "• Device icons = Different types of gadgets\n"
            "  - Phones/Tablets\n"
            "  - Computers/Laptops\n"
            "  - Smart TVs/Streaming devices\n"
            "  - Printers\n"
            "  - Smart speakers\n"
            "  - Unknown devices\n\n"
            "SECURITY USE:\n"
            "Spot devices you don't recognize! Unknown devices could be:\n"
            "• Neighbors leeching your WiFi\n"
            "• Hacked smart home devices\n"
            "• Hidden cameras or microphones\n\n"
            "ACTION: If you see unknown devices, change your WiFi password immediately!",
        ),
        HelpHotspot(
            15,
            60,
            "Device Details Table",
            "A spreadsheet view of every device connected to your network with technical details.\n\n"
            "COLUMNS EXPLAINED:\n"
            "• Device Name = Friendly name (if the device shares it)\n"
            "• IP Address = The device's 'phone number' on your network\n"
            "  - Format: 192.168.x.x (internal network only)\n"
            "• MAC Address = The device's unique hardware ID\n"
            "  - Like a fingerprint - never changes!\n"
            "• Manufacturer = Who made the device (Apple, Samsung, etc.)\n"
            "• Status = Online/Offline/Unknown\n"
            "• Last Seen = When device was last active\n\n"
            "PRO TIP: Write down MAC addresses of YOUR devices. Unknown MACs = potential intruders!",
        ),
        HelpHotspot(
            80,
            60,
            "Network Scan Controls",
            "Buttons to discover and map all devices on your network.\n\n"
            "SCAN OPTIONS:\n\n"
            "QUICK SCAN (30 seconds)\n"
            "• Checks the most common IP addresses\n"
            "• Finds most active devices quickly\n"
            "• Good for daily checks\n\n"
            "DEEP SCAN (2-5 minutes)\n"
            "• Checks every possible IP address\n"
            "• Finds hidden or quiet devices\n"
            "• Best for security audits\n\n"
            "MANUAL ADD\n"
            "• Type a specific IP address\n"
            "• Useful for adding devices that block scans\n"
            "• Good for offline devices you know about\n\n"
            "WHEN TO SCAN:\n"
            "• Weekly: Quick scan to check for intruders\n"
            "• Monthly: Deep scan full audit\n"
            "• Immediately: If you suspect someone on your network",
        ),
    ],
    "Settings": [
        HelpHotspot(
            50,
            15,
            "Settings Navigation",
            "Different categories of settings to customize Watchdog for your needs.\n\n"
            "SETTINGS CATEGORIES:\n\n"
            "NETWORK\n"
            "• WiFi connection settings\n"
            "• Network interface selection\n"
            "• Connection troubleshooting\n\n"
            "AI & MODEL\n"
            "• Choose AI model (1b, 3b, 8b, phi4)\n"
            "• Set AI response preferences\n"
            "• Configure AI behavior\n\n"
            "SECURITY\n"
            "• Firewall settings\n"
            "• Automatic blocking rules\n"
            "• Threat detection sensitivity\n\n"
            "PRIVACY\n"
            "• Data collection settings\n"
            "• Log retention policies\n"
            "• Anonymous reporting",
        ),
    ],
    "Threat Encyclopedia": [
        HelpHotspot(
            50,
            10,
            "Search Bar",
            "Quickly find specific threats by typing keywords.\n\n"
            "HOW TO USE:\n"
            "• Type any threat name (e.g., 'phishing', 'malware')\n"
            "• Type attack characteristics (e.g., 'email', 'password')\n"
            "• Results filter automatically as you type\n\n"
            "TIP: Search for 'password' to find all password-related threats!",
        ),
        HelpHotspot(
            40,
            50,
            "Threat Cards",
            "Each card explains a different cyber threat in simple terms.\n\n"
            "CARD SECTIONS:\n"
            "• Icon & Name = Quick visual identification\n"
            "• Risk Level = Critical/High/Medium severity\n"
            "• Description = What the attack does\n"
            "• Warning Signs = How to spot it happening\n"
            "• Prevention = How to protect yourself\n\n"
            "USE THIS TO:\n"
            "• Learn about new attack types\n"
            "• Identify threats you've encountered\n"
            "• Share knowledge with your team\n"
            "• Prepare security training materials",
        ),
    ],
}
