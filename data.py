import os
import cv2 as cv
from pathlib import Path

def crop_frames_using_annotations(video_path, annotation_path, fall_save_path, no_fall_save_path, image_size=224):
    '''Crop frames from video using bounding boxes in annotation file and categorize them into fall or no_fall based on the annotation.'''
    video = cv.VideoCapture(video_path)
    if not video.isOpened():
        print(f"Cannot open video {video_path}")
        return

    with open(annotation_path, "r") as file:
        fall_start_frame = None
        fall_end_frame = None

        for line_num, line in enumerate(file, start=1):
            # First two lines are for fall start and end frames
            if line_num == 1:
                fall_start_frame = int(line.strip())
                continue
            elif line_num == 2:
                fall_end_frame = int(line.strip())
                continue

            # Process remaining lines which contain bounding box data
            annotations = line.strip().split(",")
            if len(annotations) < 6:
                print(f"Malformed annotation on line {line_num} in {annotation_path}: {line.strip()}")
                continue

            try:
                frame_num = int(annotations[0])
                x_center = int(annotations[2])
                y_center = int(annotations[3])
                width = int(annotations[4])
                height = int(annotations[5])

                # Ensure bounding box values are valid
                if width <= 0 or height <= 0:
                    print(f"Invalid bounding box dimensions (width: {width}, height: {height}) on line {line_num}")
                    continue

            except ValueError as e:
                print(f"Error parsing line {line_num} in {annotation_path}: {e}")
                continue

            # Read the frame from the video
            video.set(cv.CAP_PROP_POS_FRAMES, frame_num - 1)
            ret, frame = video.read()
            if not ret:
                print(f"Cannot read frame {frame_num} from {video_path}")
                continue

            # Calculate the bounding box coordinates
            height_frame, width_frame, _ = frame.shape
            x_start = max(0, x_center - width // 2)
            y_start = max(0, y_center - height // 2)
            x_end = min(width_frame, x_center + width // 2)
            y_end = min(height_frame, y_center + height // 2)

            # Skip if the crop box is invalid
            if x_start >= x_end or y_start >= y_end:
                print(f"Invalid crop dimensions for frame {frame_num}, skipping.")
                continue

            # Crop the frame
            cropped = frame[y_start:y_end, x_start:x_end].copy()
            try:
                # Resize the cropped image
                cropped = cv.resize(cropped, (image_size, image_size), interpolation=cv.INTER_LINEAR)
                if fall_start_frame <= frame_num <= fall_end_frame:
                    img_save_path = os.path.join(fall_save_path, f"{frame_num}.jpg")
                else:
                    img_save_path = os.path.join(no_fall_save_path, f"{frame_num}.jpg")

                if not cv.imwrite(img_save_path, cropped):
                    print(f"Error saving cropped frame {frame_num}")
            except Exception as e:
                print(f"Error processing frame {frame_num}: {e}")

    video.release()

def process_all_rooms(video_and_annotation_paths, image_size=224):
    '''Process all rooms by iterating through the provided video, fall, and no_fall save paths.'''
    for video_path, fall_save_path, no_fall_save_path, annotation_path in video_and_annotation_paths:
        # Get all video files in the folder
        video_files = [f for f in os.listdir(video_path) if f.endswith('.avi')]
        
        print(f"Processing {len(video_files)} videos from {video_path}")
        
        for video_file in video_files:
            video_file_path = os.path.join(video_path, video_file)
            video_name = os.path.splitext(video_file)[0]
            annotation_file_path = os.path.join(annotation_path, f"{video_name}.txt")

            # Check if the annotation file exists
            if not os.path.isfile(annotation_file_path):
                print(f"Annotation file missing for {video_file}: Expected at {annotation_file_path}")
                continue

            # Create output directories for cropped frames (fall and no_fall)
            fall_frames_save_path = os.path.join(fall_save_path, video_name)
            no_fall_frames_save_path = os.path.join(no_fall_save_path, video_name)
            Path(fall_frames_save_path).mkdir(parents=True, exist_ok=True)
            Path(no_fall_frames_save_path).mkdir(parents=True, exist_ok=True)

            print(f"Processing {video_file} with annotation {annotation_file_path}")
            
            # Process the video and crop frames based on bounding boxes in annotations
            crop_frames_using_annotations(video_file_path, annotation_file_path, fall_frames_save_path, no_fall_frames_save_path, image_size)


if __name__ == "__main__":
    # List of (video_path, fall_save_path, no_fall_save_path, annotation_path) tuples
    video_and_annotation_paths = [
        ("datasets/FDD/Coffee_room_01/Coffee_room_01/Videos/", "datasets/FDD/Coffee_room_01/Videos_with_fall_frames/", "datasets/FDD/Coffee_room_01/Videos_with_no_fall_frames/", "datasets/FDD/Coffee_room_01/Coffee_room_01/Annotation_files/"),
        ("datasets/FDD/Coffee_room_02/Coffee_room_02/Videos/", "datasets/FDD/Coffee_room_02/Videos_with_fall_frames/", "datasets/FDD/Coffee_room_02/Videos_with_no_fall_frames/", "datasets/FDD/Coffee_room_02/Coffee_room_02/Annotation_files/"),
        ("datasets/FDD/Home_01/Home_01/Videos/", "datasets/FDD/Home_01/Videos_with_fall_frames/", "datasets/FDD/Home_01/Videos_with_no_fall_frames/", "datasets/FDD/Home_01/Home_01/Annotation_files/"),
        ("datasets/FDD/Home_02/Home_02/Videos/", "datasets/FDD/Home_02/Videos_with_fall_frames/", "datasets/FDD/Home_02/Videos_with_no_fall_frames/", "datasets/FDD/Home_02/Home_02/Annotation_files/"),
    ]
    
    # Process all rooms
    process_all_rooms(video_and_annotation_paths)
