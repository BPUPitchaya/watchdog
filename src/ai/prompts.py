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

GENERAL_PROMPT = """You are an AI assistant for WATCHDOG, a network security monitoring system. Answer the user's query helpfully and accurately.

Query: {query}

Answer:"""
