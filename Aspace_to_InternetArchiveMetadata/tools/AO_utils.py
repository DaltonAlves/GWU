# AO_utils
import requests

def get_ancestor_ref(ao_record):
    subseries_ref = None
    series_ref = None
    collection_ref = None

    ao_ancestors = ao_record['ancestors']
    for ancestor in ao_ancestors:
        level = ancestor['level']
        ref_uri = ancestor['ref']

        if level == 'subseries':
            subseries_ref = ref_uri
        elif level == 'series':
            series_ref = ref_uri
        elif level == 'recordgrp':
            collection_ref = ref_uri
        elif level == 'collection':
            collection_ref = ref_uri
        elif level == 'fonds':
            collection_ref = ref_uri

    return subseries_ref, series_ref, collection_ref

def get_location_info(ao_record, headers, host):
    instance_location = {
        'type_2': '',
        'type_3': '',
        'indicator_2': '',
        'indicator_3': '',
        'top_containerLabel': '',
        'top_containerIndicator': ''
    }
    ao_instance = ao_record['instances']
    for instance in ao_instance:
        if 'sub_container' in instance:
            sub_container = instance['sub_container']
            instance_location['type_2'] = sub_container.get('type_2', '')
            instance_location['type_3'] = sub_container.get('type_3', '')
            instance_location['indicator_2'] = sub_container.get('indicator_2', '')
            instance_location['indicator_3'] = sub_container.get('indicator_3', '')
            top_containerRef = sub_container['top_container'].get('ref')
            top_container_response = requests.get(host + top_containerRef, headers=headers) #retrieve top container record
            top_container = top_container_response.json()
            instance_location['top_containerLabel'] = top_container.get('type')
            instance_location['top_containerIndicator'] = top_container.get('indicator')


        ordered_values = [
            instance_location['top_containerLabel'],
            instance_location['top_containerIndicator'],
            instance_location['type_2'],
            instance_location['indicator_2'],
            instance_location['type_3'],
            instance_location['indicator_3']
        ]

    joined_values = ' '.join(value for value in ordered_values if value is not None)
    return joined_values


def get_notes(ao_record):
  """Extracts the type and content values of the note_singlepart JSON objects and the type and content values from the subnote objects of the note_multipart objects.

  Returns:
    A list of dictionaries, each of which contains the type and content values of a note or subnote.
  """
  notes = ao_record['notes']
  note_info = []
  for note in notes:
    if note["jsonmodel_type"] == "note_singlepart":
      note_info.append({
          "type": note["type"],
          "content": note["content"]
      })
    elif note["jsonmodel_type"] == "note_multipart":
      for subnote in note["subnotes"]:
        note_info.append({
            "type": subnote["jsonmodel_type"],
            "content": subnote["content"]
        })

  return note_info
