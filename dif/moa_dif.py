import metadata_utils as mu
from fuzzywuzzy import fuzz
import re
import time

start = time.perf_counter()

def fold_records(alma_record, dlxs_record):
    '''
    consolidates two passed records into one, filling in missing or NULL
    info from one with that from the other
    '''
    nones = (None, "None")

    folded_record = {key : (alma_record[key] if alma_record[key] not in nones else dlxs_record[key]) for key in alma_record.keys()}
    folded_record["id"] = [alma_record["id"], dlxs_record["id"]]

    return folded_record

#Reading Files

keys = mu.read_csv("id_key_test.csv")
alma = mu.read_json("alma_moa_extracted.json")
dlxs = mu.read_json("dlxs_moa_extracted.json")

#This Script:
#   -Dif on 'title' and 'year' fields (try w/ fuzzymatching)
#   -filter  post-1930(1925?) records
#   -filter non-english items
#   -output: CSV of items that passed, CSV of items that "failed"/need manual investigation

#- Doing Dif

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
    if str(key[2]) in [alma_record["id"] for alma_record in alma] and str(key[0]) in [dlxs_record["id"] for dlxs_record in dlxs]:
        alma_record = [x for x in alma if str(x["id"]) == str(key[2])][0]
        dlxs_record = [x for x in dlxs if str(x["id"]) == str(key[0])][0]

        #-got both matches, ready for tests/filtering

        #--FUZZ Title Test
        fuzz_score = None
        fuzz_score = fuzz.partial_ratio(alma_record["title"], dlxs_record["title"])
        print(f"\nfuzz score: {fuzz_score}\nalma {'title'}: {alma_record['title']}\ndlxs {'title'}: {dlxs_record['title']}", file=title_fuzz_file)
        if fuzz_score < THRESHOLD:
            investigate.append({"alma_id" : alma_record["id"], "dlxs_id" : dlxs_record["id"], "issues" : ["title"], "alma_title" : alma_record["title"], "dlxs_title" : dlxs_record["title"], "fuzz_score" : fuzz_score})

        #-Year (matching) Test
        if dlxs_record["pub_date"] != None and alma_record["pub_date"] != None and dlxs_record["pub_date"].strip("[").strip("]").strip(".").strip(",").strip("?") != alma_record['pub_date'].strip("[").strip("]").strip(".").strip(",").strip("?"):
            if alma_record["id"] + dlxs_record["id"] in [record["alma_id"] + record["dlxs_id"] for record in investigate if "alma_id" in record.keys() and "dlxs_id" in record.keys()]:
                record = [x for x in investigate if "alma_id" in x.keys() and "dlxs_id" in x.keys() and alma_record["id"] + dlxs_record["id"] == x["alma_id"] + x["dlxs_id"]][0]
                record["alma_date"] = alma_record["pub_date"]
                record["dlxs_date"] = dlxs_record["pub_date"]
                record["issues"].append("date")
            else:
                investigate.append({"alma_id":alma_record["id"], "dlxs_id" : dlxs_record["id"],"issues" : ["date"],"alma_date" : alma_record["pub_date"], "dlxs_date" : dlxs_record["pub_date"]})

        #-Language Test
        #if none
        if dlxs_record["language"] is None or alma_record["language"] is None:
            if alma_record["id"] + dlxs_record["id"] in [record["alma_id"] + record["dlxs_id"] for record in investigate if "alma_id" in record.keys() and "dlxs_id" in record.keys()]:
                record = [x for x in investigate if "alma_id" in x.keys() and "dlxs_id" in x.keys() and alma_record["id"] + dlxs_record["id"] == x["alma_id"] + x["dlxs_id"]][0]
                record["alma_langugae"] = alma_record["language"]
                record["dlxs_language"] = dlxs_record["language"]
                record["issues"].append("language")
            else:
                investigate.append({"alma_id":alma_record["id"], "dlxs_id" : dlxs_record["id"],"issues" : ["language"], "alma_language" : alma_record["language"], "dlxs_language" : dlxs_record["language"]})
        #if not english
        elif dlxs_record["language"].lower() not in ("eng", "English") or alma_record["language"].lower() not in ("eng", "English"):
            if alma_record["id"] + dlxs_record["id"] in [record["alma_id"] + record["dlxs_id"] for record in investigate if "alma_id" in record.keys() and "dlxs_id" in record.keys()]:
                record = [x for x in investigate if "alma_id" in x.keys() and "dlxs_id" in x.keys() and alma_record["id"] + dlxs_record["id"] == x["alma_id"] + x["dlxs_id"]][0]
                record["alma_langugae"] = alma_record["language"]
                record["dlxs_language"] = dlxs_record["language"]
                record["issues"].append("language")
            else:
                investigate.append({"alma_id":alma_record["id"], "dlxs_id" : dlxs_record["id"], "issues" : ["language"], "alma_language" : alma_record["language"], "dlxs_language" : dlxs_record["language"], "issues" : ["language"]})

        #-Year (Range) Test
        if dlxs_record["pub_date"] != None and alma_record["pub_date"] != None and dlxs_record["pub_date"].strip("[").strip("]").strip(".").strip(",").strip("?") == alma_record['pub_date'].strip("[").strip("]").strip(".").strip(",").strip("?"):
            try:
                test_year = int(re.findall("\d\d\d\d",dlxs_record["pub_date"])[0])
            except:
                test_year = None
            if test_year:
                if test_year > 1930:
                    if alma_record["id"] + dlxs_record["id"] in [record["alma_id"] + record["dlxs_id"] for record in investigate if "alma_id" in record.keys() and "dlxs_id" in record.keys()]:
                        record = [x for x in investigate if "alma_id" in x.keys() and "dlxs_id" in x.keys() and alma_record["id"] + dlxs_record["id"] == x["alma_id"] + x["dlxs_id"]][0]
                        record["alma_date"] = alma_record["pub_date"]
                        record["dlxs_date"] = dlxs_record["pub_date"]
                        record["issues"].append("date_range")
                    else:
                        investigate.append({"alma_id":alma_record["id"], "dlxs_id" : dlxs_record["id"], "issues" : ["date_range"], "alma_date" : alma_record["pub_date"], "dlxs_date" : dlxs_record["pub_date"]})


        if alma_record["id"] + dlxs_record["id"] not in [record["alma_id"] + record["dlxs_id"] for record in investigate if "alma_id" in record.keys() and "dlxs_id" in record.keys()]:
            passed.append(fold_records(alma_record=alma_record, dlxs_record=dlxs_record))
            passed_csv.append([alma_record["id"], dlxs_record["id"]] + [fold_records(alma_record=alma_record, dlxs_record=dlxs_record)[key] for key in headers[2:]])

#make investigate a CSV
headers = ["alma_id", "dlxs_id", "issues", "creator", "title", "pub_date", "publisher", "pub_place", "lanugage"]
investigate_csv = [headers]
fields = ["creator", "title", "pub_date", "publisher", "pub_place", "language"]
for entry in investigate:
    entry_list = [entry["alma_id"], entry["dlxs_id"], entry["issues"]]
    if "title" in entry_list[2]:
        entry_list[2] = ["title", f'fuzz_score: {entry["fuzz_score"]}']
    for alma_entry in alma:
        if alma_entry["id"] == entry_list[0]:
            for dlxs_entry in dlxs:
                if dlxs_entry["id"] == entry_list[1]:
                    entry_list.extend([alma_entry[key], dlxs_entry[key]] for key in fields)
    investigate_csv.append(entry_list)


title_fuzz_file.close

#-Writing Files

print("missing dlxs:", len(missing_dlxs), "\nmissing alma:", len(missing_alma))

mu.write_json("passed.json", passed)
mu.write_json("investigate.json", investigate)
mu.write_csv("passed.csv", passed_csv)
mu.write_csv("investigate.csv", investigate_csv)


finish = time.perf_counter()
print(f"done, completed in {finish - start}")
