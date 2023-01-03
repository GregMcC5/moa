import metadata_utils as mu
import ast

investigated = mu.read_file("investigate.csv")
fuzz_confirm_pass1 = mu.read_file("fc_passed1.csv")
no_title_pass1 = mu.read_file("no_title_passed1.csv")

headers = ["mms_id", "dlxs_id", "creator", "title", "publication_date", "publisher", "publication_place","language"]

confirmed = [(x[1:3] + [ast.literal_eval(x[i])[1] for i in range(4,10)]) if x[0] == "DLXS" else (x[1:3] + [ast.literal_eval(x[i])[0] for i in range(4,10)]) for x in investigated[1:] if x[0] in ("DLXS", "ALMA")]

confirmed.extend(fuzz_confirm_pass1 + no_title_pass1)

confirmed.insert(0,headers)
mu.write_csv("confirmed.csv", confirmed)
print("done")

