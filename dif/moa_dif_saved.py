import metadata_utils as mu
from fuzzywuzzy import fuzz

def fold_records(dlxs_record, alma_record):
    '''
    consolidates two passed records into one, filling in missing or NULL
    info from one with that from the other
    '''
    nones = (None, "None")

    folded_record = {key : (alma_record[key] if alma_record[key] not in nones else dlxs_record[key]) for key in alma_record.keys()}
    folded_record["id"] = [dlxs_record["id"], alma_record["id"]]

    return folded_record

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

THRESHOLD = 90 #<--subject to discussion/debate/reconsideration
fuzz_pass = []
passed = []
investigate = []

missing_alma = [record for record in alma if record["id"] not in [x[0] for x in keys[1:]]]
missing_marc = [record for record in marc if record["id"] not in [x[2] for x in keys[1:]]]

title_fuzz_file = open("title_fuzz_output.txt", 'w')
for key in keys:
    print(keys.index(key))
    #-verify match via keys and access
    if str(key[2]) in [marc_record["id"] for marc_record in marc] and key[0] in [alma_record["id"] for alma_record in alma]:
        for marc_record in marc:
            if str(marc_record["id"]) == str(key[2]):
                for alma_record in alma:
                    if str(alma_record["id"]) == str(key[0]):
                        #-got both matches, ready for tests/filtering

                        #--FUZZ Test
                        fuzz_score = None
                        fuzz_score = fuzz.partial_ratio(marc_record["title"], alma_record["title"])
                        print(f"\nfuzz score: {fuzz_score}\ndlxs {'title'}: {marc_record['title']}\nalma {'title'}: {alma_record['title']}", file=title_fuzz_file)
                        if fuzz_score < THRESHOLD:
                            investigate.append({"dlxs_id" : marc_record["id"], "alma_id" : alma_record["id"], "issues" : ["title"], "dlxs_title" : marc_record["title"], "alma_title" : alma_record["title"], "fuzz_score" : fuzz_score})
                        #-Year (matching) Test
                        if alma_record["pub_date"] != None and marc_record["pub_date"] != None and alma_record["pub_date"].strip("[").strip("]").strip(".").strip(",").strip("?") != marc_record['pub_date'].strip("[").strip("]").strip(".").strip(",").strip("?"):
                            if marc_record["id"] + alma_record["id"] in [record["dlxs_id"] + record["alma_id"] for record in investigate if "dlxs_id" in record.keys() and "alma_id" in record.keys()]:
                                for record in investigate:
                                    if "dlxs_id" in record.keys() and "alma_id" in record.keys() and marc_record["id"] + alma_record["id"] == record["dlxs_id"] + record["alma_id"]:
                                        record["dlxs_date"] = marc_record["pub_date"]
                                        record["alma_date"] = alma_record["pub_date"]
                                        record["issues"].append("date")
                            else:
                                investigate.append({"dlxs_id":marc_record["id"], "alma_id" : alma_record["id"],"dlxs_date" : marc_record["pub_date"], "alma_date" : alma_record["pub_date"], "issues" : ["date"]})
                        #-Language Test
                        #if none
                        if alma_record["language"] is None or marc_record["language"] is None:
                            if marc_record["id"] + alma_record["id"] in [record["dlxs_id"] + record["alma_id"] for record in investigate if "dlxs_id" in record.keys() and "alma_id" in record.keys()]:
                                for record in investigate:
                                    if "dlxs_id" in record.keys() and "alma_id" in record.keys() and marc_record["id"] + alma_record["id"] == record["dlxs_id"] + record["alma_id"]:
                                        record["dlxs_langugae"] = marc_record["language"]
                                        record["alma_language"] = alma_record["language"]
                                        record["issues"].append("language")
                            else:
                                investigate.append({"dlxs_id":marc_record["id"], "alma_id" : alma_record["id"], "dlxs_language" : marc_record["language"], "alma_language" : alma_record["language"], "issues" : ["language"]})
                        #matching test
                        elif alma_record["language"].lower() not in ("eng", "English") or marc_record["language"].lower() not in ("eng", "English"):
                            if marc_record["id"] + alma_record["id"] in [record["dlxs_id"] + record["alma_id"] for record in investigate if "dlxs_id" in record.keys() and "alma_id" in record.keys()]:
                                for record in investigate:
                                    if "dlxs_id" in record.keys() and "alma_id" in record.keys() and marc_record["id"] + alma_record["id"] == record["dlxs_id"] + record["alma_id"]:
                                        record["dlxs_langugae"] = marc_record["language"]
                                        record["alma_language"] = alma_record["language"]
                                        record["issues"].append("language")
                            else:
                                investigate.append({"dlxs_id":marc_record["id"], "alma_id" : alma_record["id"],"dlxs_language" : marc_record["language"], "alma_language" : alma_record["language"], "issues" : ["language"]})
                        if marc_record["id"] + alma_record["id"] not in [record["dlxs_id"] + record["alma_id"] for record in investigate if "dlxs_id" in record.keys() and "alma_id" in record.keys()]:
                            passed.append(fold_records(dlxs_record=marc_record, alma_record=alma_record))



title_fuzz_file.close

#-------No Longer in Use---------
#--strict (non-fuzzy) filtering--
#--------------------------------
#sort on basis of title matching,year matching, dumping into either of the two groups below


# for key in keys:
#     #-verify match via keys and access
#     if str(key[2]) in [marc_record["id"] for marc_record in marc] and key[0] in [alma_record["id"] for alma_record in alma]:
#         for marc_record in marc:
#             if str(marc_record["id"]) == str(key[2]):
#                 for alma_record in alma:
#                     if str(alma_record["id"]) == str(key[0]):
#                         #-title check
#                         #-ALMA titles are looking like they tend to be shorter, so I'm doing 'in' tests, checking with ALMA title in MARC title
#                         if alma_record["title"].strip().lower() not in marc_record["title"].strip().lower():
#                             investigate.append([val for val in marc_record.values()])
#                         else:
#                             strict_title_pass_counter += 1


# print(f"{strict_title_pass_counter} out of {len(keys)} passed the initial scrict title test")

#print(f"{year_pass_counter} passed the year test")

#output:
#2216 out of 9981 passed the initial strict title test
#9922 out of 9981 passed the initial fuzz test
#3 pased the year test <--- I'm realizing that something odd is going on with the ALMA dates, (they're all from the mid-2000s) taking a look at this and will report.
    #updated the ALMA content with more correct ALMA pub_date data; should be good now!

print("missing alma:", len(missing_alma), "\nmissing marc:", len(missing_marc))
print(missing_marc, missing_alma)

mu.write_json("passed.json", passed)
mu.write_json("investigate.json", investigate)


print("done")
