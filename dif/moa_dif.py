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

#-------------------
#--title fuzz test--
#-------------------
#gets fuzzy score between correspnoding DLXS and ALMA titles, and prints them (w/ score)
#to title_fuzz_output.txt. We can review that doc to assess the success of the fuzzy apporach.

THRESHOLD = 75 #<--subject to discussion/debate/reconsideration
fuzz_pass = []

title_fuzz_file = open("title_fuzz_output.txt", 'w')
for key in keys:
    print(keys.index(key))
    #-verify match via keys and access
    if str(key[2]) in [marc_record["id"] for marc_record in marc] and key[0] in [alma_record["id"] for alma_record in alma]:
        for marc_record in marc:
            if str(marc_record["id"]) == str(key[2]):
                for alma_record in alma:
                    if str(alma_record["id"]) == str(key[0]):
                        #-write fuzz score w/ title
                        fuzz_score = fuzz.partial_ratio(marc_record["title"], alma_record["title"])
                        print(f"\nfuzz score: {fuzz_score}\nmarc {'title'}: {marc_record['title']}\nalma {'title'}: {alma_record['title']}", file=title_fuzz_file)
                        if fuzz_score > THRESHOLD:
                            fuzz_pass.append(val for val in marc_record.values())

title_fuzz_file.close

#--------------------------------
#--strict (non-fuzzy) filtering--
#--------------------------------
#sort on basis of title matching,year matching, dumping into either of the two groups below
passed = []
investigate = []
strict_title_pass_counter = 0
year_pass_counter = 0

for key in keys:
    #-verify match via keys and access
    if str(key[2]) in [marc_record["id"] for marc_record in marc] and key[0] in [alma_record["id"] for alma_record in alma]:
        for marc_record in marc:
            if str(marc_record["id"]) == str(key[2]):
                for alma_record in alma:
                    if str(alma_record["id"]) == str(key[0]):
                        #-title check
                        #-ALMA titles are looking like they tend to be shorter, so I'm doing 'in' tests, checking with ALMA title in MARC title
                        if alma_record["title"].strip().lower() not in marc_record["title"].strip().lower():
                            investigate.append([val for val in marc_record.values()])
                        else:
                            strict_title_pass_counter += 1

                        #-year check
                        if alma_record["pub_date"].strip() != marc_record['pub_date'].strip():
                            print(alma_record["pub_date"], marc_record['pub_date'])
                            investigate.append([val for val in marc_record.values()])
                        else:
                            year_pass_counter += 1


print(f"{strict_title_pass_counter} out of {len(keys)} passed the initial scrict title test")
print(f"{len(fuzz_pass)} out of {len(keys)} passed the initial fuzz test")

print(f"{year_pass_counter} passed the year test")

#output:
#2216 out of 9981 passed the initial strict title test
#9922 out of 9981 passed the initial fuzz test
#3 pased the year test <--- I'm realizing that something odd is going on with the ALMA dates, (they're all from the mid-2000s) taking a look at this and will report.
    #updated the ALMA content with more correct ALMA pub_date data; should be good now!
print("done")