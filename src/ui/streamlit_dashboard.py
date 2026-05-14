import streamlit as st
import json
import pandas as pd
import os
import sys

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.ml.feature_extractor import FeatureExtractor
import joblib

# Load ML model and extractor
try:
    model = joblib.load('models/random_forest_model.pkl')
    extractor = FeatureExtractor()
except Exception as e:
    st.error(f"Failed to load ML model: {e}")
    model = None
    extractor = None

st.set_page_config(page_title="WATCHDOG AI Dashboard", layout="wide")

st.title("WATCHDOG AI Dashboard")

# Sidebar
st.sidebar.title("Navigation")
st.sidebar.write("Real-time Network Security Monitor")

# Main metrics
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("System Status", "SAFE", "Operational")

with col2:
    threat_level = 0.2  # This would be calculated from data
    threat_label = "LOW" if threat_level < 0.3 else "MEDIUM" if threat_level < 0.7 else "HIGH"
    st.metric("Threat Level", f"{threat_label} ({threat_level:.2f})")

with col3:
    # Refresh button
    if st.button("Refresh Data"):
        st.rerun()

# Load packet data
try:
    with open('packet_data.json', 'r') as f:
        data = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    data = {"packets": [], "alerts": []}

packets = data.get("packets", [])
alerts = data.get("alerts", [])

# Traffic visualization
st.subheader("Network Traffic")
if packets:
    packet_count = len(packets)
    st.metric("Total Packets Captured", packet_count)
    
    # Display recent packets
    recent_packets = packets[-10:]  # Last 10 packets
    if recent_packets:
        df = pd.DataFrame(recent_packets)
        st.dataframe(df, use_container_width=True)
    else:
        st.write("No recent packets to display")
else:
    st.metric("Total Packets Captured", 0)
    st.write("No packet data available. Start the sniffer to collect data.")

# Alerts section
if alerts:
    st.subheader("Recent Alerts")
    for alert in alerts[-5:]:  # Last 5 alerts
        st.warning(f"Alert: {alert}")

# AI Chat section
st.subheader("AI Assistant")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "AI", 
        "content": "Hello! I'm the AI assistant for WATCHDOG. I can help with threat analysis, packet predictions, and system status. Try commands like 'threat level' or 'predict: src_ip=192.168.1.1 dst_ip=10.0.0.1 protocol=tcp'."
    })

# Display chat messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Chat input
if prompt := st.chat_input("Ask me about network security..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Process the command
    response = process_command(prompt)
    
    # Add AI response
    st.session_state.messages.append({"role": "assistant", "content": response})
    
    st.rerun()

def process_command(msg):
    """Process user commands and return responses."""
    msg_lower = msg.lower()
    
    if not model or not extractor:
        return "ML model not available. Please ensure models/random_forest_model.pkl exists."
    
    if "hi" in msg_lower or "hello" in msg_lower or "hey" in msg_lower or "greetings" in msg_lower:
        return "Hello! I'm the AI assistant for WATCHDOG. I can help with threat analysis, packet predictions, and system status. Try commands like 'threat level' or 'predict: src_ip=X dst_ip=Y protocol=tcp'."
    
    elif "threat" in msg_lower and "level" in msg_lower:
        threat_level = 0.2  # In a real implementation, calculate from current data
        threat_text = "LOW" if threat_level < 0.3 else "MEDIUM" if threat_level < 0.7 else "HIGH"
        return f"Current threat level: {threat_text} ({threat_level:.2f})"
    
    elif "status" in msg_lower:
        return "System status: SAFE - All systems operational."
    
    elif "alert" in msg_lower:
        if alerts:
            return f"Recent alerts: {len(alerts)} detected. Latest: {alerts[-1] if alerts else 'None'}"
        else:
            return "No recent alerts detected."
    
    elif msg_lower.startswith("predict"):
        # Parse prediction parameters
        try:
            params_str = msg.split(":", 1)[1].strip() if ":" in msg else ""
            if not params_str:
                return "Usage: predict: src_ip=X dst_ip=Y protocol=tcp src_port=A dst_port=B"
            
            # Parse parameters
            params = {}
            for pair in params_str.split():
                if "=" in pair:
                    key, value = pair.split("=", 1)
                    params[key.strip()] = value.strip()
            
            # Create packet data
            packet_data = {
                'src_ip': params.get('src_ip', '192.168.1.1'),
                'dst_ip': params.get('dst_ip', '10.0.0.1'),
                'protocol': 6 if params.get('protocol', 'tcp').lower() == 'tcp' else 17,
                'length': int(params.get('length', '100')),
                'src_port': int(params.get('src_port', '12345')),
                'dst_port': int(params.get('dst_port', '80')),
                'flags': params.get('flags', 'S'),
                'direction': 'inbound'
            }
            
            # Extract features and predict
            features = extractor.extract_packet_features(packet_data)
            selected_features = extractor.get_selected_features(features)
            features_array = np.array(selected_features).reshape(1, -1)
            prediction = model.predict(features_array)[0]
            
            label_map = {0: 'NORMAL', 1: 'ATTACK'}
            predicted_label = label_map.get(prediction, 'UNKNOWN')
            
            return f"ML Prediction for packet {packet_data['src_ip']}:{packet_data['src_port']} -> {packet_data['dst_ip']}:{packet_data['dst_port']}: {predicted_label}"
            
        except Exception as e:
            return f"Error processing prediction: {str(e)}. Usage: predict: src_ip=X dst_ip=Y protocol=tcp src_port=A dst_port=B"
    
    else:
        return "I'm not sure what you mean. Try asking about the system status, current threats, or predicting packet risks with commands like 'threat level' or 'predict: src_ip=X dst_ip=Y protocol=tcp'."
