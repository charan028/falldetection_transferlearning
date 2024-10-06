import os
import shutil
import random

def create_dataset_structure(base_dir):
    """
    Create the folder structure for train, val, and test datasets.
    """
    for split in ['train', 'val', 'test']:
        for category in ['fall', 'no_fall']:
            os.makedirs(os.path.join(base_dir, split, category), exist_ok=True)

def collect_images_from_dirs(directories, extensions=('.jpg', '.png')):
    """
    Collect images from multiple directories with specified extensions.
    
    Args:
        directories: List of directories to collect images from.
        extensions: Tuple of allowed image file extensions.
    
    Returns:
        List of image file paths.
    """
    files = []
    for directory in directories:
        for root, _, filenames in os.walk(directory):  # Recursively walk through directories
            for file in filenames:
                if file.lower().endswith(extensions):
                    files.append(os.path.join(root, file))
        print(f"Found {len(files)} images in {directory}")
    return files

def split_data(source_fall_dirs, source_no_fall_dirs, dest_base_dir, train_ratio=0.7, val_ratio=0.15):
    """
    Split the data from multiple fall and no_fall directories into train, val, and test directories.
    
    Args:
        source_fall_dirs: List of directories containing fall frames
        source_no_fall_dirs: List of directories containing no_fall frames
        dest_base_dir: Destination directory to store the train, val, test split
        train_ratio: Ratio of data to be used for training
        val_ratio: Ratio of data to be used for validation
    """
    # Collect all fall and no_fall frames from multiple directories
    fall_files = collect_images_from_dirs(source_fall_dirs)
    no_fall_files = collect_images_from_dirs(source_no_fall_dirs)

    # Debugging: Check if files exist in both categories
    if len(no_fall_files) == 0:
        print("No files found in no_fall directories!")
        return

    if len(fall_files) == 0:
        print("No files found in fall directories!")
        return

    # Shuffle the data
    random.shuffle(fall_files)
    random.shuffle(no_fall_files)

    # Compute split sizes
    total_fall = len(fall_files)
    total_no_fall = len(no_fall_files)

    train_fall = int(train_ratio * total_fall)
    val_fall = int(val_ratio * total_fall)
    
    train_no_fall = int(train_ratio * total_no_fall)
    val_no_fall = int(val_ratio * total_no_fall)

    # Split fall data
    train_fall_files = fall_files[:train_fall]
    val_fall_files = fall_files[train_fall:train_fall + val_fall]
    test_fall_files = fall_files[train_fall + val_fall:]

    # Split no_fall data
    train_no_fall_files = no_fall_files[:train_no_fall]
    val_no_fall_files = no_fall_files[train_no_fall:train_no_fall + val_no_fall]
    test_no_fall_files = no_fall_files[train_no_fall + val_no_fall:]

    # Debug: Print split sizes
    print(f"Training set: {len(train_fall_files)} fall, {len(train_no_fall_files)} no_fall")
    print(f"Validation set: {len(val_fall_files)} fall, {len(val_no_fall_files)} no_fall")
    print(f"Test set: {len(test_fall_files)} fall, {len(test_no_fall_files)} no_fall")

    # Move files into the appropriate directories
    for file in train_fall_files:
        shutil.copy(file, os.path.join(dest_base_dir, 'train', 'fall', os.path.basename(file)))
    
    for file in val_fall_files:
        shutil.copy(file, os.path.join(dest_base_dir, 'val', 'fall', os.path.basename(file)))

    for file in test_fall_files:
        shutil.copy(file, os.path.join(dest_base_dir, 'test', 'fall', os.path.basename(file)))

    for file in train_no_fall_files:
        shutil.copy(file, os.path.join(dest_base_dir, 'train', 'no_fall', os.path.basename(file)))

    for file in val_no_fall_files:
        shutil.copy(file, os.path.join(dest_base_dir, 'val', 'no_fall', os.path.basename(file)))

    for file in test_no_fall_files:
        shutil.copy(file, os.path.join(dest_base_dir, 'test', 'no_fall', os.path.basename(file)))

# Paths to your current folders with fall and no_fall frames for multiple categories
source_fall_dirs = [
    'datasets/FDD/Coffee_room_01/Videos_with_fall_frames/',
    'datasets/FDD/Coffee_room_02/Videos_with_fall_frames/',
    'datasets/FDD/Home_01/Videos_with_fall_frames/',
    'datasets/FDD/Home_02/Videos_with_fall_frames/'
]

source_no_fall_dirs = [
    'datasets/FDD/Coffee_room_01/Videos_with_no_fall_frames/',
    'datasets/FDD/Coffee_room_02/Videos_with_no_fall_frames/',
    'datasets/FDD/Home_01/Videos_with_no_fall_frames/',
    'datasets/FDD/Home_02/Videos_with_no_fall_frames/'
]

# Destination base directory for the new structure
dest_base_dir = 'fall_detection_data'

# Create the dataset folder structure
create_dataset_structure(dest_base_dir)

# Split and move the data
split_data(source_fall_dirs, source_no_fall_dirs, dest_base_dir)
