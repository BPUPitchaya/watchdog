"""Ollama auto-installer for cross-platform setup."""

import os
import platform
import shutil
import subprocess
import sys
import tempfile
import urllib.request


class OllamaInstaller:
    """Handles automatic Ollama installation and setup."""

    def __init__(self, model="llama3.2:1b"):
        self.model = model
        self.platform = platform.system()
        self.arch = platform.machine()

    def is_ollama_installed(self):
        """Check if Ollama is already installed."""
        try:
            result = subprocess.run(
                ["ollama", "--version"], capture_output=True, text=True, timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def is_ollama_running(self):
        """Check if Ollama service is running."""
        try:
            import requests

            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False

    def install_ollama(self):
        """Install Ollama based on platform."""
        if self.is_ollama_installed():
            print("Ollama is already installed.")
            return True

        print(f"Installing Ollama for {self.platform}...")

        if self.platform == "Darwin":  # macOS
            return self._install_macos()
        elif self.platform == "Linux":
            return self._install_linux()
        elif self.platform == "Windows":
            return self._install_windows()
        else:
            print(f"Unsupported platform: {self.platform}")
            return False

    def _install_macos(self):
        """Install Ollama on macOS."""
        try:
            # Download Ollama for macOS
            url = "https://ollama.ai/download/Ollama-darwin.zip"
            print(f"Downloading Ollama from {url}...")

            with tempfile.TemporaryDirectory() as temp_dir:
                zip_path = os.path.join(temp_dir, "Ollama-darwin.zip")
                urllib.request.urlretrieve(url, zip_path)

                # Extract
                import zipfile

                with zipfile.ZipFile(zip_path, "r") as zip_ref:
                    zip_ref.extractall(temp_dir)

                # Move to Applications
                app_path = os.path.join(temp_dir, "Ollama.app")
                dest_path = "/Applications/Ollama.app"

                if os.path.exists(app_path):
                    shutil.move(app_path, dest_path)
                    print("Ollama installed to /Applications/Ollama.app")
                    print("Please start Ollama from Applications and run this script again.")
                    return True
                else:
                    print("Error: Ollama.app not found in extracted files")
                    return False

        except Exception as e:
            print(f"Error installing Ollama on macOS: {e}")
            print("Manual installation: Download from https://ollama.ai/download")
            return False

    def _install_linux(self):
        """Install Ollama on Linux."""
        try:
            print("Installing Ollama using official install script...")
            # Use official Ollama install script
            install_cmd = "curl -fsSL https://ollama.ai/install.sh | sh"
            result = subprocess.run(install_cmd, shell=True, check=True)

            if result.returncode == 0:
                print("Ollama installed successfully.")
                return True
            else:
                print("Ollama installation failed.")
                return False

        except Exception as e:
            print(f"Error installing Ollama on Linux: {e}")
            print("Manual installation: curl -fsSL https://ollama.ai/install.sh | sh")
            return False

    def _install_windows(self):
        """Install Ollama on Windows."""
        try:
            # Download Windows installer
            url = "https://ollama.ai/download/OllamaSetup.exe"
            print(f"Downloading Ollama installer from {url}...")

            temp_dir = tempfile.gettempdir()
            installer_path = os.path.join(temp_dir, "OllamaSetup.exe")
            urllib.request.urlretrieve(url, installer_path)

            print(f"Installer downloaded to: {installer_path}")
            print("Please run the installer manually, then restart this script.")
            print(f"Or run: start {installer_path}")

            # Optionally auto-run installer
            try:
                os.startfile(installer_path)
            except:
                pass

            return True

        except Exception as e:
            print(f"Error downloading Ollama for Windows: {e}")
            print("Manual installation: Download from https://ollama.ai/download")
            return False

    def pull_model(self):
        """Pull the required AI model."""
        if not self.is_ollama_installed():
            print("Ollama is not installed. Please install it first.")
            return False

        try:
            print(f"Pulling model {self.model}...")
            result = subprocess.run(
                ["ollama", "pull", self.model], capture_output=True, text=True, timeout=300
            )  # 5 minute timeout

            if result.returncode == 0:
                print(f"Model {self.model} pulled successfully.")
                return True
            else:
                print(f"Error pulling model: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            print("Model pull timed out. The model may be large.")
            return False
        except Exception as e:
            print(f"Error pulling model: {e}")
            return False

    def is_model_available(self):
        """Check if the model is already available."""
        try:
            result = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=5)
            return self.model in result.stdout
        except:
            return False

    def setup(self, auto_install=False):
        """
        Complete setup process.

        Args:
            auto_install: If True, automatically install Ollama if missing

        Returns:
            bool: True if setup successful, False otherwise
        """
        print("Checking Ollama installation...")

        # Check if installed
        if not self.is_ollama_installed():
            if auto_install:
                print("Ollama not found. Installing...")
                if not self.install_ollama():
                    print("Failed to install Ollama automatically.")
                    print("Please install manually from https://ollama.ai/download")
                    return False
            else:
                print("Ollama not found. Please install from https://ollama.ai/download")
                return False

        # Check if running
        if not self.is_ollama_running():
            print("Ollama is installed but not running.")
            print("Please start Ollama application/service.")
            if self.platform == "Darwin":
                print("On macOS: Open Ollama from Applications")
            elif self.platform == "Windows":
                print("On Windows: Start Ollama from Start Menu")
            elif self.platform == "Linux":
                print("On Linux: Run 'ollama serve' in terminal")
            return False

        # Check model
        if not self.is_model_available():
            print(f"Model {self.model} not found. Pulling...")
            if not self.pull_model():
                print("Failed to pull model.")
                return False

        print(f"Ollama setup complete! Model {self.model} is ready.")
        return True


def main():
    """Main entry point for standalone installer."""
    import argparse

    parser = argparse.ArgumentParser(description="Ollama Auto-Installer")
    parser.add_argument("--model", default="llama3.2:3b", help="Model to pull")
    parser.add_argument(
        "--auto-install", action="store_true", help="Automatically install Ollama if missing"
    )

    args = parser.parse_args()

    installer = OllamaInstaller(model=args.model)
    success = installer.setup(auto_install=args.auto_install)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
