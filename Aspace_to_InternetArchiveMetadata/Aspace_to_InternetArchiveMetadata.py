import re
import requests
import pandas as pd
from urllib.parse import urlparse
import user.config as config
from user.auth import UserAuthenticator
from tools.mediaType import MediaTypeResolver
from tools.AO_utils import get_ancestor_ref, get_location_info, get_notes
from tools.csvtool import check_nested_key_value, read_csv_to_dict

# Set your CSV file path here:
sheet = 'example.csv'

# Pre-set values used for all collection material uploaded to IA. Don't touch these. 
IA_sponsor = 'George Washington University Libraries'
IA_collection = "gwulibraries"

def clean_part_of(part_of):
    # Remove repeating values (e.g., "MSXXXX (MSXXXX) Series 1 Series 1")
    # The regex pattern captures a word or identifier and looks ahead for the same word with optional text in between. Still doesn't handle (MSXXXX) MSXXXX
    cleaned = re.sub(r'\b(\w+)\b(?: \(\1\))?(?: \1)+', r'\1', part_of)
    return cleaned

if __name__ == "__main__":
    authenticator = UserAuthenticator()

    if authenticator.headers:
        print("Authentication successful. Session headers:", authenticator.headers)
    else:
        print("Authentication failed.")
    
    headers = authenticator.headers
    HOST = config.HOST

    input_data = read_csv_to_dict(sheet)
    
    for item in input_data:
        if item['archival_object_source'] == '':
            print('empty row')
            continue  # Continue to the next item instead of breaking the loop

        print('Starting: ' + item['file'])

        # Extracting AO_ID from URL
        parsed_url = urlparse(item['archival_object_source'])
        domain = parsed_url.netloc
        ao_id = None
        
        if "archivesspace" in domain:
            match = re.search('.+archival_object_(\d+)$', item['archival_object_source'])
            if match:
                ao_id = match.group(1)
                archival_object_source = config.PUI + 'archival_objects/' + ao_id
                item.update({'archival_object_source': archival_object_source})
        elif "searcharchives" in domain:
            match =  re.search(r'/(\d+)$', item['archival_object_source'])
            if match:
                ao_id = match.group(1)
            archival_object_source = item['archival_object_source']
            item.update({'archival_object_source': archival_object_source})
        else:
            print("Error! Please check your archival_object URL in the CSV sheet for: " + item['file'])
            continue

        if not ao_id:
            print(f"Could not extract AO_ID for: {item['file']}")
            continue

        # Retrieving AO record JSON
        ao_record_response = requests.get(f"{HOST}/repositories/2/archival_objects/{ao_id}", headers=headers)
        if ao_record_response.status_code == 404:
            print(f"Archival object couldn't be retrieved: {item['archival_object_source']}")
            continue
        ao_record = ao_record_response.json()

        # Setting ref_id as identifier-bib
        ref_id = ao_record.get('ref_id', 'N/A')
        item.update({'identifier-bib': f"{ref_id} (ref_id)"})

        # Setting title
        item.update({'title': ao_record.get('title', '')})

        # Setting dates
        ao_dates = ao_record.get('dates', [])
        ao_dateExpression = ao_dateStart = ao_dateEnd = ''
        if ao_dates:
            first_date = ao_dates[0]
            ao_dateExpression = first_date.get('expression', '')
            ao_dateStart = first_date.get('begin', '')
            ao_dateEnd = first_date.get('end', '')
        item.update({'date': ao_dateStart, 'date_expression': ao_dateExpression})

        # Getting ancestor refs
        subseries_ref, series_ref, collection_ref = get_ancestor_ref(ao_record)
        
        subseriesTitle = subseriesID = ''
        if subseries_ref:
            ao_subseries = requests.get(HOST + subseries_ref, headers=headers).json()
            subseriesTitle = ao_subseries.get('title', '')
            subseriesID = ao_subseries.get('component_id', '')

        seriesTitle = seriesID = ''
        if series_ref:
            ao_series = requests.get(HOST + series_ref, headers=headers).json()
            seriesTitle = ao_series.get('title', '')
            seriesID = ao_series.get('component_id', '')

        ao_collection = requests.get(HOST + collection_ref, headers=headers).json()
        collectionTitle = ao_collection.get('title', '')
        collectionID = ao_collection.get('id_0', '')

        # AO instance and location info
        location_info = get_location_info(ao_record, headers, config.HOST)
        full_location = " ".join(filter(None, [seriesID, subseriesID, location_info]))
        part_of = f"{collectionTitle} ({collectionID}) {full_location}"
        item.update({'part_of': clean_part_of(part_of)})

        # Finding agents at collection level to use as creator
        creator_found = False
        collectionAgents = ao_collection.get('linked_agents', [])
        for agent in collectionAgents:
            if agent['role'] in ['creator', 'source']:
                creator_ref = agent['ref']
                creator_record = requests.get(HOST + creator_ref, headers=headers).json()
                creator_name = creator_record.get('title', '')
                item.update({'creator': creator_name})
                creator_found = True
                break

        if not creator_found:
            print(f"Collection record,{collectionTitle}, has no linked creator agent records!")

        # Check for rights statement at collection level
        if check_nested_key_value(ao_collection, "type", "userestrict"):
            rights = []
            for note in ao_collection.get("notes", []):
                if note.get("type") == "userestrict":
                    for subnote in note.get("subnotes", []):
                        rights.append(subnote['content'])
            item.update({'rights': ' '.join(rights)})
        else:
            print(f"{collectionTitle} does not have a rights statement (key-value pair 'type': 'userestrict')")

        # Match file extension to IA media type
        media_type_resolver = MediaTypeResolver()
        media_type = media_type_resolver.get_media_type(item)
        if media_type:
            item.update({'mediatype': media_type})

        # Pulling AO notes for IA description fields
        note_list = get_notes(ao_record)
        for count, note in enumerate(note_list, 1):
            description = note.get('content')
            if isinstance(description, str):
                item.update({f'description[{count}]': description})
            elif isinstance(description, list):
                for desc in description:
                    item.update({f'description[{count}]': desc})
                    count += 1

        # Setting pre-set values
        item.update({'sponsor': IA_sponsor, 'collection': IA_collection})

        # Setting IA subject values
        item.update({'subject[1]': collectionID, 'subject[2]': '', 'subject[3]': ''})
        print(item)

    df = pd.DataFrame(input_data)
    df.to_csv('update.csv', index=False)

    print("All done!")
