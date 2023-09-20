import re
import requests
import pandas as pd
import csv
import json
from urllib.parse import urlparse
import user.config as config
from user.auth import UserAuthenticator
from tools.mediaType import MediaTypeResolver
from tools.AO_utils import get_ancestor_ref, get_location_info
from tools.csvtool import check_nested_key_value, read_csv_to_dict
import os

#to do:
    #regex for part_of
    #think through csv required fields. How does "identifier" and "file" relate to context of workflows? file is just file or URI? Look a old upload sheets.
    #need to strip the archival_object row from updated CSV because it'll mess up the upload to IA. Or we could prefer PUI links and push those as part of IA metadata. 
    #cleanup part_of citation. need to regex out repeating values (ex (MSxxxx) MSxxxx Series 1 Series 1)
    #think through mapping of aspace notes (scope/content, extent)

#set your CSV file path here:
sheet = 'C:/Users/dalton_alves/Desktop/example.csv'

#pre-set values. don't touch these. they are used for all collection material uploaded to IA
IA_sponsor = 'George Washington University Libraries'
IA_collection = "gwulibraries"

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
    print('Starting: ' + item['file'])
    
    #extracting AO_ID from URL of archival object in staff interface
    parsed_url = urlparse(item['archival_object'])
    domain = parsed_url.netloc
    if "archivesspace" in domain:
        match = re.search('.+archival_object_(\d+)$', item['archival_object'])
        if match:
            ao_id = match.group(1)
            print(ao_id)
    else:
        print("Please update CSV to link to PUI (you are currently linking to the public interface or an invalid URL) for: " + item)
        pass

    ao_record = requests.get(HOST + '/repositories/2/archival_objects/' + ao_id, headers=headers)
    if ao_record.status_code == 404:
        raise Exception('This archival object couldn\'t be retrieved with the api. Something may be wrong with the URL?: ' + ['archival_object'])
    else:
        ao_record = ao_record.json()

    ao_title = ao_record['title']
    item.update({'title': ao_title})

    ao_dates = ao_record['dates']
    if ao_dates:  # Use this check to see if the list is not empty
        for dates in ao_dates:
            ao_dateExpression = dates['expression']
            ao_dateStart = dates.get('begin', '')  
            ao_dateEnd = dates.get('end', '')   
            break
    else:
        ao_dateExpression = ''
        ao_dateStart = ''
        ao_dateEnd = ''
        ao_dateEnd = ''
    item.update({'date':ao_dateStart})
    item.update({'date_range':ao_dateExpression})

    #get ref of ancestor records of AO
    subseries_ref, series_ref, collection_ref = get_ancestor_ref(ao_record)
    
    if subseries_ref is not None:
        ao_subseries = requests.get(HOST + subseries_ref, headers=headers)
        ao_subseries = ao_subseries.json()
        subseriesTitle = ao_subseries['title']
        subseriesID = ao_subseries['component_id']
    if subseries_ref is None: #this could be else statement I think?
        subseriesTitle = ''
        subseriesID = ''

    if series_ref is not None:
        ao_series =  requests.get(HOST + series_ref, headers=headers)
        ao_series = ao_series.json()
        seriesTitle = ao_series['title']
        seriesID = ao_series['component_id']
    if series_ref is None: #this could be else statement I think?
        seriesTitle = ''
        seriesID = ''
    #don't need IF statements here because I think every AO should be connected to a collection record
    ao_collection =  requests.get(HOST + collection_ref, headers=headers)
    ao_collection = ao_collection.json()
    collectionTitle = ao_collection['title']
    collectionID = ao_collection['id_0']

    ##ao instance and location info
    location_info = get_location_info(ao_record, headers, config.HOST)

    full_location = " ".join(filter(None, [seriesID, subseriesID, location_info]))
    part_of = collectionTitle + " (" + collectionID + ") " + full_location #need to use regex here to clean up; fix bad data entry like "MSXXXX Series 1 Series"
    # Remove repetitions of words using regular expressions
    item.update({'part_of':part_of})


    #finding agents at colleciton level to use as creator
    creator_found = False #setting for print message
    collectionAgents = ao_collection['linked_agents']
    for agent in collectionAgents:
        role = agent['role']
        ref = agent['ref']

        if role == 'creator' or role == 'source':
            creator_ref = ref
            creator_found = True #updating flag for print message
            creator_record = requests.get(HOST + creator_ref, headers=headers)
            creator_record = creator_record.json()
            creator_name =  creator_record['title']
            item.update({'creator':creator_name})
        else:
            pass
    if not creator_found:
        print(collectionTitle + " has no creator record!")


    #check for rights statement at collection level
    if check_nested_key_value(ao_collection, "type", "userestrict"):
        rights = []
        for note in ao_collection["notes"]:
            if note.get("type") == "userestrict":
                for subnote in note.get("subnotes"):
                    rights = subnote['content']
        item.update({'rights':rights})
    else:
        print(collectionTitle + " does not have a rights statement (key-value pair 'type': 'userestrict')")


    #match file extension to controlled vocabular used by IA for mediatype (this is a required field)
    media_type_resolver = MediaTypeResolver()
    media_type = media_type_resolver.get_media_type(item)
    if media_type:
        item.update({'mediatype': media_type})

    #setting pre-set values
    item.update({'sponsor': IA_sponsor})
    item.update({'collection': IA_collection})
    
    #setting IA subject values. These will require user input in the updated CSV. Archival description uses LC and other controlled vocabularies but they are often applied to the resource record. Does not map well to the vocabulary we use for IA objects.
    item.update({'subject[1]': collectionID}) #we consistently use the collectionID of material as a subject heading in IA
    item.update({'subject[2]': ''})
    item.update({'subject[3]': ''})
    #setting description. Can update this later to relate to map to archival description, but need to think through logic. Possibly maping to AO notes for scope and content at series and or file/item level.
    item.update({'description': ''})

    #constructing source_URI to PUI from the AO_ID
    source_uri = config.PUI + 'archival_objects/' + ao_id
    item.update({'source_uri'})
    
df = pd.DataFrame(input_data)
df.to_csv('update.csv', index=False)

print("All done!")
