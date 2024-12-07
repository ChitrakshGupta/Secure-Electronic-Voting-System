import face_recognition
import cv2
import os
import numpy as np

# Directory containing reference images
PHOTO_FOLDER = "photos"

# Load known faces
def load_user_face(photo_folder, user_id):
    """
    Load a single user's face encoding based on their user ID.

    Args:
        photo_folder (str): Path to the folder containing photos.
        user_id (str): The user ID to locate the photo.

    Returns:
        tuple: Face encoding and user ID, or (None, None) if not found.
    """
    photo_filename = f"{user_id}.jpg"  # Assume photo filenames follow the format "<user_id>.jpg"
    image_path = os.path.join(photo_folder, photo_filename)

    if not os.path.exists(image_path):
        return None, None

    image = face_recognition.load_image_file(image_path)
    face_encodings = face_recognition.face_encodings(image)

    if face_encodings:
        return face_encodings[0], user_id
    else:
        print(f"No face detected in {photo_filename}.")
        return None, None


# Capture a photo from the camera
def capture_photo():
    print("Press 'Space' to capture a photo or 'q' to quit.")
    video_capture = cv2.VideoCapture(0)

    while True:
        ret, frame = video_capture.read()
        if not ret:
            print("Failed to capture image. Exiting.")
            break

        # Show the camera feed
        cv2.imshow("Camera", frame)

        # Wait for user to press 'Space' to capture or 'q' to quit
        key = cv2.waitKey(1)
        if key == ord(' '):  # Space bar
            photo = frame
            break
        elif key == ord('q'):  # 'q' to quit
            photo = None
            break

    video_capture.release()
    cv2.destroyAllWindows()
    return photo

# Match the captured photo with known faces
def match_face(captured_photo, known_face_encodings, known_face_names):
    captured_face_locations = face_recognition.face_locations(captured_photo)
    captured_face_encodings = face_recognition.face_encodings(captured_photo, captured_face_locations)

    for captured_encoding in captured_face_encodings:
        matches = face_recognition.compare_faces(known_face_encodings, captured_encoding)
        face_distances = face_recognition.face_distance(known_face_encodings, captured_encoding)

        if matches:
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                return known_face_names[best_match_index], face_distances[best_match_index]
    
    return None, None

