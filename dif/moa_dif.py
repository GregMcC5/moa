import metadata_utils as mu
from fuzzywuzzy import fuzz

def fold_records(alma_record, dlxs_record):
    '''
    consolidates two passed records into one, filling in missing or NULL
    info from one with that from the other
    '''
    nones = (None, "None")

    folded_record = {key : (alma_record[key] if alma_record[key] not in nones else dlxs_record[key]) for key in alma_record.keys()}
    folded_record["id"] = [alma_record["id"], dlxs_record["id"]]

    return folded_record

keys = mu.read_csv("id_key_test.csv")
alma = mu.read_json("alma_moa_extracted.json")
dlxs = mu.read_json("dlxs_moa_extracted.json")

#This Script:
#   -Dif on 'title' and 'year' fields (try w/ fuzzymatching)
#   -filter  post-1930(1925?) records
#   -filter non-english items
#   -output: CSV of items that passed, CSV of items that "failed"/need manual investigation
#   -check if ALMA records lack info

#-------------------
#--title fuzz test--
#-------------------
#gets fuzzy score between correspnoding alma and dlxs titles, and prints them (w/ score)
#to title_fuzz_output.txt. We can review that doc to assess the success of the fuzzy apporach.

THRESHOLD = 90 #<--subject to discussion/debate/reconsideration
fuzz_pass = []
passed = []
headers = ["alma_id", "dlxs_id", "creator", "title", "pub_date", "pub_place", "language"]
passed_csv = [[headers]]
investigate = []

missing_dlxs = [record for record in dlxs if record["id"] not in [x[0] for x in keys[1:]]]
missing_alma = [record for record in alma if record["id"] not in [x[2] for x in keys[1:]]]

title_fuzz_file = open("title_fuzz_output.txt", 'w')
for key in keys:
    print(keys.index(key))
    #-verify match via keys and access
    if str(key[2]) in [alma_record["id"] for alma_record in alma] and key[0] in [dlxs_record["id"] for dlxs_record in dlxs]:
        for alma_record in alma:
            if str(alma_record["id"]) == str(key[2]):
                for dlxs_record in dlxs:
                    if str(dlxs_record["id"]) == str(key[0]):
                        #-got both matches, ready for tests/filtering

                        #--FUZZ Test
                        fuzz_score = None
                        fuzz_score = fuzz.partial_ratio(alma_record["title"], dlxs_record["title"])
                        print(f"\nfuzz score: {fuzz_score}\nalma {'title'}: {alma_record['title']}\ndlxs {'title'}: {dlxs_record['title']}", file=title_fuzz_file)
                        if fuzz_score < THRESHOLD:
                            investigate.append({"alma_id" : alma_record["id"], "dlxs_id" : dlxs_record["id"], "issues" : ["title"], "alma_title" : alma_record["title"], "dlxs_title" : dlxs_record["title"], "fuzz_score" : fuzz_score})
                        #-Year (matching) Test
                        if dlxs_record["pub_date"] != None and alma_record["pub_date"] != None and dlxs_record["pub_date"].strip("[").strip("]").strip(".").strip(",").strip("?") != alma_record['pub_date'].strip("[").strip("]").strip(".").strip(",").strip("?"):
                            if alma_record["id"] + dlxs_record["id"] in [record["alma_id"] + record["dlxs_id"] for record in investigate if "alma_id" in record.keys() and "dlxs_id" in record.keys()]:
                                for record in investigate:
                                    if "alma_id" in record.keys() and "dlxs_id" in record.keys() and alma_record["id"] + dlxs_record["id"] == record["alma_id"] + record["dlxs_id"]:
                                        record["alma_date"] = alma_record["pub_date"]
                                        record["dlxs_date"] = dlxs_record["pub_date"]
                                        record["issues"].append("date")
                            else:
                                investigate.append({"alma_id":alma_record["id"], "dlxs_id" : dlxs_record["id"],"alma_date" : alma_record["pub_date"], "dlxs_date" : dlxs_record["pub_date"], "issues" : ["date"]})
                        #-Language Test
                        #if none
                        if dlxs_record["language"] is None or alma_record["language"] is None:
                            if alma_record["id"] + dlxs_record["id"] in [record["alma_id"] + record["dlxs_id"] for record in investigate if "alma_id" in record.keys() and "dlxs_id" in record.keys()]:
                                for record in investigate:
                                    if "alma_id" in record.keys() and "dlxs_id" in record.keys() and alma_record["id"] + dlxs_record["id"] == record["alma_id"] + record["dlxs_id"]:
                                        record["alma_langugae"] = alma_record["language"]
                                        record["dlxs_language"] = dlxs_record["language"]
                                        record["issues"].append("language")
                            else:
                                investigate.append({"alma_id":alma_record["id"], "dlxs_id" : dlxs_record["id"], "alma_language" : alma_record["language"], "dlxs_language" : dlxs_record["language"], "issues" : ["language"]})
                        #language test
                        elif dlxs_record["language"].lower() not in ("eng", "English") or alma_record["language"].lower() not in ("eng", "English"):
                            if alma_record["id"] + dlxs_record["id"] in [record["alma_id"] + record["dlxs_id"] for record in investigate if "alma_id" in record.keys() and "dlxs_id" in record.keys()]:
                                for record in investigate:
                                    if "alma_id" in record.keys() and "dlxs_id" in record.keys() and alma_record["id"] + dlxs_record["id"] == record["alma_id"] + record["dlxs_id"]:
                                        record["alma_langugae"] = alma_record["language"]
                                        record["dlxs_language"] = dlxs_record["language"]
                                        record["issues"].append("language")
                            else:
                                investigate.append({"alma_id":alma_record["id"], "dlxs_id" : dlxs_record["id"],"alma_language" : alma_record["language"], "dlxs_language" : dlxs_record["language"], "issues" : ["language"]})
                        if alma_record["id"] + dlxs_record["id"] not in [record["alma_id"] + record["dlxs_id"] for record in investigate if "alma_id" in record.keys() and "dlxs_id" in record.keys()]:
                            passed.append(fold_records(alma_record=alma_record, dlxs_record=dlxs_record))
                            passed_csv.append([alma_record["id"], dlxs_record["id"]] + [fold_records(alma_record=alma_record, dlxs_record=dlxs_record)[key] for key in headers[2:]])



title_fuzz_file.close

#-------No Longer in Use---------
#--strict (non-fuzzy) filtering--
#--------------------------------
#sort on basis of title matching,year matching, dumping into either of the two groups below


# for key in keys:
#     #-verify match via keys and access
#     if str(key[2]) in [alma_record["id"] for alma_record in alma] and key[0] in [dlxs_record["id"] for dlxs_record in dlxs]:
#         for alma_record in alma:
#             if str(alma_record["id"]) == str(key[2]):
#                 for dlxs_record in dlxs:
#                     if str(dlxs_record["id"]) == str(key[0]):
#                         #-title check
#                         #-dlxs titles are looking like they tend to be shorter, so I'm doing 'in' tests, checking with dlxs title in alma title
#                         if dlxs_record["title"].strip().lower() not in alma_record["title"].strip().lower():
#                             investigate.append([val for val in alma_record.values()])
#                         else:
#                             strict_title_pass_counter += 1


# print(f"{strict_title_pass_counter} out of {len(keys)} passed the initial scrict title test")

#print(f"{year_pass_counter} passed the year test")

#output:
#2216 out of 9981 passed the initial strict title test
#9922 out of 9981 passed the initial fuzz test
#3 pased the year test <--- I'm realizing that something odd is going on with the dlxs dates, (they're all from the mid-2000s) taking a look at this and will report.
    #updated the dlxs content with more correct dlxs pub_date data; should be good now!

print("missing dlxs:", len(missing_dlxs), "\nmissing alma:", len(missing_alma))
print(missing_alma, missing_dlxs)

mu.write_json("passed.json", passed)
mu.write_json("investigate.json", investigate)
mu.write_csv("passed.csv", passed_csv)


print("done")
