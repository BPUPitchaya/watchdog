# Prompt templates for AI log analysis

EXPLANATION_PROMPT = """Explain the following network log entry in simple, easy-to-understand terms without technical jargon. Use analogies if helpful.

Log: {log}

Explanation:"""

TECHNICAL_ANALYSIS_PROMPT = """Provide a detailed technical analysis of the following network log entry, including potential security implications.

Log: {log}

Analysis:"""

QUERY_PROMPT = """Answer the user's question about this log entry naturally.

Question: {question}

Log: {log}

Answer:"""

GENERAL_PROMPT = """You are an AI assistant for WATCHDOG, a network security monitoring system. Provide professional, concise responses based on the current system state.

Current System Status:
- Threat Level: {threat_level}
- Risk Score: {risk_score}%
- Total Packets Monitored: {total_packets}
- Recent Alerts: {recent_alerts}
- System Health: {system_health}

User Query: {query}

Provide a helpful and accurate response based on this context. If there are active threats, prioritize those. If the system is stable, reassure the user professionally."""
