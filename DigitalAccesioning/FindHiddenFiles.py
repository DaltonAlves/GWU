import os

def identify_hidden_items(directory):
    for root, dirs, files in os.walk(directory):
        # Check for hidden directories
        hidden_dirs = [d for d in dirs if d.startswith('.')]
        for hidden_dir in hidden_dirs:
            hidden_dir_path = os.path.join(root, hidden_dir)
            print(f"Hidden directory found: {hidden_dir_path}")

        # Check for hidden files
        hidden_files = [f for f in files if f.startswith('.')]
        for hidden_file in hidden_files:
            hidden_file_path = os.path.join(root, hidden_file)
            print(f"Hidden file found: {hidden_file_path}")

# Replace 'your_directory_path' with the path of the directory you want to search
directory_path = r''

identify_hidden_items(directory_path)