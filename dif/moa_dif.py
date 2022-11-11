import dif.metadata_utils as mu
from fuzzywuzzy import fuzz


keys = mu.read_csv("id_key_test.csv")
marc = mu.read_json("MARC_moa_extracted.json")
alma = mu.read_json("ALMA_moa_extracted.json")


#This Script:
#   -Dif on 'title' and 'year' fields (try w/ fuzzymatching)
#   -filter  post-1930(1925?) records
#   -filter non-english items
#   -output: CSV of items that passed, CSV of items that "failed"/need manual investigation