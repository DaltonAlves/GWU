import json
import re
import os


class MediaTypeResolver:
    MEDIA_TYPES_FILENAME = os.path.join(os.path.dirname(__file__), 'extension_to_mediatype.json')
    
    def __init__(self):
        with open(MediaTypeResolver.MEDIA_TYPES_FILENAME, 'r') as json_file:
            self.media_types = json.load(json_file)
    
    def get_media_type(self, item):
        if 'file' in item:
            file = item['file']  # Assuming item is a dictionary containing the 'file' key
            match = re.search(r'\.(.+)$', file)

            if match:
                extension = match.group(1) #convert to lowercase just in case
                if extension in self.media_types:
                    return self.media_types[extension]
                else:
                    print('No media type match')
                    return ''  # Return a default value or handle the case when extension is not in the dictionary
            else:
                print('regex failed or no file information present in CSV')
                return None  # Return None if the regex match fails
        else:
            print('No "file" key in the dictionary')
            return None
