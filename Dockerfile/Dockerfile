services:
  watchdog-app:
    build: .
    network_mode: "host"  # Crucial: Allows sniffing real Wi-Fi/Ethernet
    environment:
      - DISPLAY=${DISPLAY} # Shares your screen with Docker
    volumes:
      - /tmp/.X11-unix:/tmp/.X11-unix # Shared socket for the GUI
    depends_on:
      - ollama-brain

  ollama-brain:
    image: ollama/ollama
    ports:
      - "11434:11434"
    volumes:
      - ./ollama_storage:/root/.ollama