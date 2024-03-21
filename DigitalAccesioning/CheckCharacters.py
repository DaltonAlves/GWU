import re
import json
from pathlib import Path

def get_unique_name(path, new_name):
    counter = 1
    while (path / new_name).exists():
        base, ext = new_name.stem, new_name.suffix
        new_name = f"{base}({counter}){ext}"
        counter += 1
    return new_name

def remove_spaces(directory):
    for path in directory.rglob('*'):
        if path.is_file() and " " in path.name:
            new_name = path.with_name(path.name.replace(" ", "_"))
            if path != new_name:
                print(f'Old filename: {path.name}')
                print(f'New filename: {new_name.name}')
                new_name = directory / get_unique_name(directory, new_name)
                user_confirmation = input('Do you want to rename this file? (y/n): ').strip().lower()
                if user_confirmation == 'y':
                    try:
                        path.rename(new_name)
                        print(f'Renamed: {path.name} to {new_name.name}')
                    except Exception as e:
                        print(f'Error renaming {path.name}: {e}')
                else:
                    print(f'Skipped: {path.name}')
        elif path.is_dir() and " " in path.name:
            new_name = path.with_name(path.name.replace(" ", "_"))
            if path != new_name:
                print(f'Old directory name: {path.name}')
                print(f'New directory name: {new_name.name}')
                new_name = directory / get_unique_name(directory, new_name)
                user_confirmation = input('Do you want to rename this directory? (y/n): ').strip().lower()
                if user_confirmation == 'y':
                    try:
                        path.rename(new_name)
                        print(f'Renamed: {path.name} to {new_name.name}')
                    except Exception as e:
                        print(f'Error renaming {path.name}: {e}')
                else:
                    print(f'Skipped: {path.name}')

def identify_bad_characters(directory_path):
    bad_characters = []

    for path in directory_path.rglob('*'):
        if any(ord(char) > 127 for char in path.name):
            bad_characters.append({"file_path": str(path.relative_to(directory_path)), "file_name": path.name})

    json_file_path = directory_path / "bad_characters.json"

    try:
        with json_file_path.open("w", encoding="utf-8") as json_file:
            json.dump(bad_characters, json_file, ensure_ascii=False, indent=2)
        print(f"Bad characters saved to {json_file_path}")
    except Exception as e:
        print(f'Error saving bad characters to JSON: {e}')

if __name__ == "__main__":
    directory_path = Path(r'')  # Provide your directory path here
    remove_spaces(directory_path)
    identify_bad_characters(directory_path)