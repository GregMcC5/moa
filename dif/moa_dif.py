import metadata_utils as mu
from fuzzywuzzy import fuzz

#Curtis, if you're running this script locally, you may need to get the fuzzywuzzy library for it to successfully run;
#here's the documentation on it here: https://pypi.org/project/fuzzywuzzy/; you should just be able to 'pip install fuzzywuzzy' with it on the command line

keys = mu.read_csv("id_key_test.csv")
marc = mu.read_json("MARC_moa_extracted.json")
alma = mu.read_json("ALMA_moa_extracted.json")

#This Script:
#   -Dif on 'title' and 'year' fields (try w/ fuzzymatching)
#   -filter  post-1930(1925?) records
#   -filter non-english items
#   -output: CSV of items that passed, CSV of items that "failed"/need manual investigation


#--title fuzz test--
#gets fuzzy score between correspnoding DLXS and ALMA titles, and prints them (w/ score)
#to title_fuzz_output.txt. We can review that doc to assess the success of the fuzzy apporach.
title_fuzz_file = open("title_fuzz_output.txt", 'w')
for key in keys:
    print(key)
    #-verify match via keys
    if str(key[2]) in [marc_record["id"] for marc_record in marc] and key[0] in [alma_record["id"] for alma_record in alma]:
        for marc_record in marc:
            if str(marc_record["id"]) == str(key[2]):
                for alma_record in alma:
                    if str(alma_record["id"]) == str(key[0]):
                        #write fuzz score w/ title
                        fuzz_score = fuzz.partial_ratio(marc_record["title"], alma_record["title"])
                        print(f"\nfuzz score: {fuzz_score}\nmarc {'title'}: {marc_record['title']}\nalma {'title'}: {alma_record['title']}", file=title_fuzz_file)
title_fuzz_file.close
print('done')
