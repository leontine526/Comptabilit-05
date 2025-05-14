import subprocess
import sys
import os

def setup_spacy():
    """Setup spaCy model for French language"""
    print("Setting up spaCy model for French language...")
    
    try:
        # Check if the model is already installed
        model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fr_core_web_sm")
        if os.path.exists(model_path):
            print("spaCy model already installed.")
            return True
        
        # Download small French model
        subprocess.check_call([sys.executable, "-m", "spacy", "download", "fr_core_web_sm"])
        print("spaCy model for French language installed successfully!")
        return True
    except Exception as e:
        print(f"Error installing spaCy model: {str(e)}")
        return False

if __name__ == "__main__":
    setup_spacy()