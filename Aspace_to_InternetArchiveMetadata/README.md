# ArchivesSpace to Internet Archive Metadata
Repurposes archival description from GWU's ArchivesSpace records to facilitate digital collection metadata creation. Maps metadata from Aspace 'archival object' records (AOs) and their ancestors (resource and other AO records) to required and additional custom fields in the Internet Archive's [metadata schema](https://archive.org/developers/metadata-schema/index.html).

Also maps the file extension of a digital object to the required 'mediatype' IA field and its related [controlled vocabulary](https://help.archive.org/help/file-formats/). 

# How to use

+ Clone this repository to your local machine.
+ Update user/config.py with your Aspace login and Aspace API URL.
+ Copy the example CSV and match digital file URIs, file names, and the URL of their representative archival object record in Aspace. Make sure that the URL is from the staff interface, not the PUI.
+ Update the "sheet" variable in Aspace_to_InternetArchiveMetadata.py to point to your updated CSV.
+ Run TitleAspace_to_InternetArchiveMetadata.py.
+ Your ouput will save as update.csv in the same directory as Aspace_to_InternetArchiveMetadata.py. 
    
## CSV 
+ identifier = file name without the file extension (Examples = ms2373_s2_c107D_f7_i1 ; mvc0044_s1_c7_film15) 
+ file = file name + extension. do not include file path (Examples = ms2373_s2_c107D_f7_i1.mp4 ; mvc0044_s1_c7_film15.mp4)
+ source_uri = the URL of the archival_object record in the public user interface (Example = https://searcharchives.library.gwu.edu/repositories/2/archival_objects/342462)



