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
            print("match:", match)
        elif len(match) > 1:
            print("\n\nsomething bad happened\n\n")
            print(match)
            match = None
        if match:
            scores = []
            if len(match.keys()) > 2:
                ocr_content = [val for key,val in match.items() if "tpg" in key]
                for ocr in ocr_content:
                    scores.append(fuzz.partial_ratio(record[3].lower().strip(), ocr.lower()))
                top_score = max(scores)
                print(top_score)


print(fail_counter)
print("done")



