# ArchivesSpace Digital Object Record Creator Tool
Updated version of the classic GW SCRC Aspace Digital Object Record Creator.

This version allows for users to choose between a user-generated titled for a DO record or to simply inherent a title from the attached archival object record. 
    
## CSV setup
+ new title (optional) = If this field is left blank, the title of the digital object will be inherited from the linked archival object. You can use this field if you'd like the title to be different from the archival object. 
+ file_uri = the URI of the related digital object. For preservation copies, this should point to the location of the preservation server. For access copies, the URI is the link to the digital object in a digital repository.
+ archival_object_source = the URL of the archival object which the digital object record will be linked to. This AO link can either be from the PUI or staff interface.
+ publish_link = set FALSE for preservation copies; set TRUE for access copies. This "publish" refers the publication status of the URI in the DO record. It does not refer to if the DO record itself is published.
+ xlink_actuate_attribute = "onLoad" (don't change this)
+ xlink_show_attribute = "new" (don't change this)

## To do:
+ Update to set publish status of DO record (not URI subrecord).
+ Add handling for multiple file URIs


