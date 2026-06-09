import sys
import os
import time
import joblib
import pandas as pd
import numpy as np

# watchdog root directory to system path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ai.ollama_client import OllamaClient
from src.ml.feature_extractor import FeatureExtractor

SELECTED_FEATURES = [
    'src_bytes', 'same_srv_rate', 'flag', 'dst_host_serror_rate', 
    'serror_rate', 'diff_srv_rate', 'dst_host_same_srv_rate', 
    'srv_serror_rate', 'dst_host_srv_serror_rate', 'dst_host_same_src_port_rate',
    'dst_host_diff_srv_rate', 'count', 'dst_bytes', 'dst_host_srv_diff_host_rate',
    'protocol_type', 'srv_count', 'dst_host_srv_count', 'service', 
    'dst_host_rerror_rate', 'dst_host_count'
]

def run_latency_profile(iterations=50):
    model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models', 'random_forest_model.pkl')
    
    model = joblib.load(model_path)
    extractor = FeatureExtractor()
    ai_client = OllamaClient(model="llama3.2:1b")
    
    ml_times = []
    xai_times = []
    total_times = []
    
    print(f"Starting latency profiling ({iterations} iterations)...")
    
    sample_packet = {'src_ip': '192.168.1.1', 'dst_ip': '10.0.0.1', 'protocol': 'TCP', 'length': 100}
    
    for i in range(iterations):
        # Time ML
        start_ml = time.perf_counter()
        features = extractor.extract_packet_features(sample_packet)
        df_full = pd.DataFrame([features]) #convert to DataFrame
        df_selected = df_full[SELECTED_FEATURES] #filter to only the features the model expects
        
        prediction = model.predict(df_selected)
        end_ml = time.perf_counter()
        
        # Time XAI
        start_xai = time.perf_counter()
        explanation = ai_client.query("Analyze this network threat")
        end_xai = time.perf_counter()
        
        ml_times.append(end_ml - start_ml)
        xai_times.append(end_xai - start_xai)
        total_times.append(end_xai - start_ml)
        
    print(f"\n=== LATENCY PROFILING RESULTS ===")
    print(f"Avg ML Inference: {np.mean(ml_times):.4f}s")
    print(f"Avg XAI Generation: {np.mean(xai_times):.4f}s")
    print(f"Avg Total System Latency: {np.mean(total_times):.4f}s")
    
    return total_times

if __name__ == "__main__":
    run_latency_profile()