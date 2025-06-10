import cv2
import face_recognition
import pickle
import os
import sys
from pathlib import Path


def ensure_data_dirs():
    """Ensure all required directories exist."""
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/Capture_Images", exist_ok=True)


def find_encoding(images_list):
    """Extract face encodings from a list of images."""
    encode_list = []
    for img in images_list:
        try:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(img)

            if not face_locations:
                print(f"Warning: No face found in one of the images")
                continue

            encode = face_recognition.face_encodings(img, face_locations)[0]
            encode_list.append(encode)
        except Exception as e:
            print(f"Error encoding image: {str(e)}")
            continue

    return encode_list


def main():
    """Main function to process images and generate encodings."""
    # Importing Employee images into a list
    folder_path = 'Images'
    if not os.path.exists(folder_path) or not os.listdir(folder_path):
        print(f"Error: Images folder not found or empty at {os.path.abspath(folder_path)}")
        sys.exit(1)

    image_paths = os.listdir(folder_path)
    print(f"Found {len(image_paths)} images in {folder_path}")

    img_list = []
    employee_ids = []
    for path in image_paths:
        img_path = os.path.join(folder_path, path)
        img = cv2.imread(img_path)
        if img is None:
            print(f"Warning: Could not read image {img_path}")
            continue

        img_list.append(img)
        employee_ids.append(os.path.splitext(path)[0])

    print(f"Processing {len(employee_ids)} images with IDs: {employee_ids}")

    print("Encoding Started...")
    encode_list_known = find_encoding(img_list)
    encode_list_known_with_ids = [encode_list_known, employee_ids]
    print("Encoding Complete")

    # Make sure data directory exists
    ensure_data_dirs()

    # Save in both locations for backward compatibility
    file = open("EncodedImages.pickle", "wb")
    pickle.dump(encode_list_known_with_ids, file)
    file.close()

    data_path = os.path.join("data", "EncodedImages.pickle")
    file = open(data_path, "wb")
    pickle.dump(encode_list_known_with_ids, file)
    file.close()

    print(f"Encoded files saved to:\n- {os.path.abspath('EncodedImages.pickle')}\n- {os.path.abspath(data_path)}")


if __name__ == "__main__":
    main()
