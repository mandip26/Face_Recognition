import os
import shutil

def ensure_data_paths():
    """Ensure that all required paths exist and files are copied to the correct locations."""
    # Create required directories
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/Capture_Images", exist_ok=True)

    # If EncodedImages.pickle exists in root but not in data folder, copy it
    if os.path.exists("EncodedImages.pickle") and not os.path.exists("data/EncodedImages.pickle"):
        shutil.copy("EncodedImages.pickle", "data/EncodedImages.pickle")
        print("Copied EncodedImages.pickle to data directory")

    # Return True if encoded images file exists in either location
    return os.path.exists("EncodedImages.pickle") or os.path.exists("data/EncodedImages.pickle")
