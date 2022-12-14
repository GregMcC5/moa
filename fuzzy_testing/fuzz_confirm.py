import metadata_utils as mu
from fuzzywuzzy import fuzz

THRESHOLD = 50

tpg_content = mu.read_file("tpg_content_full.json") + mu.read_file("tpg_content_full2.json")
passed_records = mu.read_file("passed.csv")

fail_counter = 0


tpg_ids = [x["dlps_id"] for x in tpg_content]

#comparing it with current OCR contetn
for record in passed_records[1:]:
    if record[1] in tpg_ids:
        record_scores = []
        match = [y for y in tpg_content if y["dlps_id"] == record[1]]
        if len(match) == 1:
            match = match[0]
            #print("match:", match)
        elif len(match) > 1:
            print("\n\nsomething bad happened\n\n")
            #print(match)
            match = None
        if match:
            scores = []
            if len(match.keys()) > 2:
                #ocr_content = {key : val for key,val in match.items() if "tpg" in key}
                for key, val in {key : val for key,val in match.items() if "tpg" in key}.items():
                    scores.append([fuzz.partial_ratio(record[3], val), key, val])
                top_score = sorted(scores,key=lambda x:x[0], reverse=True)[0]
                if record[1] == "ABK8873.0006.001":
                    print(top_score, record[3])
                with open("fuzz_output.txt", 'a') as file:
                    file.write(f"{record[3]}\nfuzz score: {top_score[0]}, title page index:? {key}\nid: {record[1]}\n\n")


print(fail_counter)

print("fuzz_test example:", fuzz.partial_ratio("American history,", "\nI LLU STRATED\nWITIH NUMEROUS MAPS AND ENGRAVINGS.\nREVO)iT oiI     THO E c[ ) GLO)N IES.\nN~~~~ )2~or~~~:.\n2l\n~odu; o    &inc\n\n\n\n"))

print("done")


# First Round of Fuzz Results (using .strip() and .lower()):
#   - 100   : 101
#   - 99-90 : 3075
#   - 89-80 : 2618
#   - 79-70 : 917
#   - 69-60 : 615
#   - 59-50 : 325
#   - 49-40 : 345
#   - 39-30 : 123
#   - 29-20 : 41
#   - 19-10 : 15
#   -  9-0  : 20

# Second Round of Fuzz Results (using neither .strip() or .lower()):
#   - 100   : 1
#   - 99-90 : 46
#   - 89-80 : 57
#   - 79-70 : 73
#   - 69-60 : 124
#   - 59-50 : 240
#   - 49-40 : 1038
#   - 39-30 : 1320
#   - 29-20 : 2557
#   - 19-10 : 2688
#   -  9-0  : 51