# ArchivesSpace to Internet Archive Metadata
Repurposes archival description from GWU's ArchivesSpace records to facilitate digital collection metadata creation. 

**How to use**

+ Clone this repository to your local machine.
+ Update user/config.py with your Aspace login and Aspace API URL.
+ Copy the example CSV and match files, file names, and the URL of their representative archival object record in Aspace. Make sure that the URL is from the staff interface, not the PUI.
+ Update the "sheet" variable in [Title](Aspace_to_InternetArchiveMetadata.py) to point to your updated CSV.
+ Run [Title](Aspace_to_InternetArchiveMetadata.py)
+ Your ouput will save as update.csv in the same directory as [Title](Aspace_to_InternetArchiveMetadata.py). 
    