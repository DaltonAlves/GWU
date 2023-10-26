import re
import requests
import pandas as pd
import csv
import json
from urllib.parse import urlparse
import user.config as config
from user.auth import UserAuthenticator
from tools.mediaType import MediaTypeResolver
from tools.AO_utils import get_ancestor_ref, get_location_info, get_notes
from tools.csvtool import check_nested_key_value, read_csv_to_dict
import os

#to do:
    #regex for part_of
    #think through csv required fields. How does "identifier" and "file" relate to context of workflows? file is just file or URI? Look a old upload sheets.
    #need to strip the archival_object row from updated CSV because it'll mess up the upload to IA. Or we could prefer PUI links and push those as part of IA metadata. 
    #cleanup part_of citation. need to regex out repeating values (ex (MSxxxx) MSxxxx Series 1 Series 1)
    #think through mapping of aspace notes (scope/content, extent)
    #is there any value of having mediatype map to a specific pre-defined profile for different material types?

#set your CSV file path here:
sheet = 'C:/Users/Dalton_alves/Desktop/example.csv'

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
    if item['archival_object_source'] == '':
        print('empty row')
        break
    print('Starting: ' + item['file'])

    #extracting AO_ID from URL of archival object in staff interface or public user interface
    parsed_url = urlparse(item['archival_object_source'])
    domain = parsed_url.netloc
    if "archivesspace" in domain:
        match = re.search('.+archival_object_(\d+)$', item['archival_object_source'])
        if match:
            ao_id = match.group(1)
            #constructing archival_object_source to PUI from the AO_ID
            archival_object_source = config.PUI + 'archival_objects/' + ao_id
            item.update({'archival_object_source': archival_object_source})
    elif "searcharchives" in domain:
        match =  re.search(r'/(\d+)$', item['archival_object_source'])
        if match:
            ao_id = match.group(1)
        source_uri = item['archival_object_source']
        item.update({'archival_object_source': source_uri})
    else:
        print("Error! Please check your archival_object URL in the CSV sheet for: " + item['file'])
        pass
    
    #retrieving ao_record json
    ao_record = requests.get(HOST + '/repositories/2/archival_objects/' + ao_id, headers=headers)
    if ao_record.status_code == 404:
        raise Exception('This archival object couldn\'t be retrieved with the api. Something may be wrong with the URL?: ' + ['archival_object'])
    else:
        ao_record = ao_record.json()

    #setting title
    ao_title = ao_record['title']
    item.update({'title': ao_title})

    #setting dates
    ao_dates = ao_record['dates']
    if ao_dates:  # Use this to check to see if the list is not empty
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

    #get ref of ancestor records of AO and grabbing titles and component IDs.
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
        ao_series = requests.get(HOST + series_ref, headers=headers)
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
    part_of = collectionTitle + " (" + collectionID + ") " + full_location #need to use regex here to clean up; fix bad data entry like "MSXXXX (MSXXXX) Series 1 Series..."
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


    #match file extension to controlled vocabulary used by IA for mediatype (this is a required field)
    media_type_resolver = MediaTypeResolver()
    media_type = media_type_resolver.get_media_type(item)
    if media_type:
        item.update({'mediatype': media_type})

    #pulling AO notes from ao record and setting as IA "description" fields
    note_list = get_notes(ao_record)
    descriptioncount = 1 #count will be used to create description[1], description[2], ect per IA upload instructions for multiple descriptions. 
    for note in note_list:
        description = note.get('content')
        if type(description) == str:
            item.update({'description' + '[' + str(descriptioncount) + ']':description}) 
            descriptioncount += 1
        if type(description) == list:
            for x in description: #probably a better variable than x here. 
                item.update({'description' + '[' + str(descriptioncount) + ']':x}) 
                descriptioncount += 1


    #setting pre-set values
    item.update({'sponsor': IA_sponsor})
    item.update({'collection': IA_collection})
    
    #setting IA subject values. These will require user input in the updated CSV. Archival description uses LC and other controlled vocabularies but they are often applied to the resource record. Does not map well to the vocabulary we use for IA objects.
    item.update({'subject[1]': collectionID}) #we consistently use the collectionID of material as a subject heading in IA
    item.update({'subject[2]': ''})
    item.update({'subject[3]': ''})

df = pd.DataFrame(input_data)
df.to_csv('update.csv', index=False)

print("All done!")
