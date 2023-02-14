import metadata_utils as mu
import ast

investigated = mu.read_file("investigate.csv")
fuzz_confirm_pass1 = mu.read_file("fc_passed1.csv")
no_title_pass1 = mu.read_file("no_title_passed1.csv")
fp_r2pass = mu.read_file("fp_second_round_pass.csv")
notpg_r2pass = mu.read_file("notpg_r2_passed.csv")
r3_main = mu.read_file("r3_checked.csv")
r3_incorrect = mu.read_file("r3_incorrect.csv")
r3_publishers = mu.read_file("round3_test_with_publishers.csv")
r3_missing = mu.read_file("r3_missings.csv")

just_publishers = [[x[3], x[-3]] for x in r3_publishers]

r3_main_confirmed = [x[4:] for x in r3_main[1:] if "y" in x[0].lower()]
r3_missings_confirmed = [x[4:] for x in r3_missing if "y" in x[0].lower()]
r3_missings_incorrect_ids = [x[5] for x in r3_missing if "n" in x[0].lower()]
r3_incorrect_ids = [x[5] for x in r3_main if "n" in x[0].lower()]
print(len(r3_incorrect_ids))
r3_incorrect_confirmed = [[x[1]] + [x[0]] + x[2:] for x in r3_incorrect if x[0] in r3_incorrect_ids]
r3_missing_incorrect_confirmed = [[x[1]] + [x[0]] + x[2:] for x in r3_incorrect if x[0] in r3_missings_incorrect_ids]

r3_corrected = []
for record in r3_main_confirmed:
    if record[1] in [x[0] for x in just_publishers]:
        match = [x for x in just_publishers if x[0] == record[1]][0]
        r3_corrected.append(record[:5] + [match[1]] + record[5:])

headers = ["mms_id", "dlxs_id", "creator", "title", "publication_date", "publisher", "publication_place","language"]

confirmed = [(x[1:3] + [ast.literal_eval(x[i])[1] for i in range(4,10)]) if x[0] == "DLXS" else (x[1:3] + [ast.literal_eval(x[i])[0] for i in range(4,10)]) for x in investigated[1:] if x[0] in ("DLXS", "ALMA")] + r3_corrected + r3_incorrect_confirmed + r3_missings_confirmed + r3_missing_incorrect_confirmed

confirmed.extend(fuzz_confirm_pass1 + no_title_pass1 + fp_r2pass + notpg_r2pass)

confirmed.insert(0,headers)
mu.write_csv("confirmed.csv", confirmed)
print("done")

