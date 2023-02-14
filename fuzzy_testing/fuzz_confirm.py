import metadata_utils as mu
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import pytesseract as pyt
import os.path
import os


THRESHOLD = 75


#tpg_content = mu.read_file("tpg_content_full.json") + mu.read_file("tpg_content_full2.json")
tpg_content = mu.read_file("tpg_content_new_approach_full.json")
passed_records = mu.read_file("passed_2.csv")

no_title_page_identified = 0

first_round_passed_counter = 0
first_round_fail_counter = 0
second_round_pass_counter = 0
second_round_fail_counter = 0
not_in_there = 0
lost_counter = 0


passed_first = []
full_paths = []
re_ocr_success = []
no_title_page = []
second_round_fail = []
second_round_pass = []

tpg_ids = [x["dlps_id"] for x in tpg_content]


#----Round 1 Check----
#comparing it with current OCR content
for record in passed_records[1:]:
    if record[1] in tpg_ids:
        match = [y for y in tpg_content if y["dlps_id"] == record[1]]
        if len(match) == 1:
            match = match[0]
        elif len(match) > 1:
            print("\n\nsomething bad happened\n\n")
            match = None
        if match:
            if len(match.keys()) > 2:
                selection, score = process.extractOne(query=record[3],choices=[key + "||" + val for key, val in match.items() if "tpg" in key], scorer=fuzz.partial_ratio)
                page = selection.split("||")[0]
                ocr = selection.split("||")[1]
                # #-Doing some testing
                if record[1] == "ABK8873.0001.001":
                    print(f'''
                    score: {score}
                    title: {record[3]}
                    page : {page}
                    ocr : {ocr}
                    ''')
                # #-appending to a text file
                with open("fuzz_output.txt", 'a') as file:
                    file.write(f"{record[3]}\nfuzz score: {score}, title page index:? {page}\nid: {record[1]}\n\n")
                #-checking score, appending
                if score >= THRESHOLD:
                    passed_first.append(record) # to be added to confirmed
                    first_round_passed_counter += 1
                elif score < THRESHOLD:
                #----Round 2 Check----
                    first_round_fail_counter += 1
                    #-write filenames
                    root = record[1]
                    path = f"/n1/obj/{root[0].lower()}/{root[1].lower()}/{root[2].lower()}/{root.lower()}/{page.strip('tpg - ').lower()}"
                    full_paths.append(path)
                    # with open("need_filepathes.txt", 'a') as file:
                    #     file.write(path + "\n")

                    #-check for filepath, do re-OCR

                    img_files = os.listdir("moa_batch_2.nosync")
                    file_name = path.split("/")[-2:]
                    file_name = "-".join(file_name)
                    print(file_name)
                    if file_name in img_files:
                        new_score = process.extractOne(record[3],[pyt.image_to_string("moa_batch_2.nosync/" + file_name)], scorer=fuzz.partial_ratio)[1]
                        print("extracted")
                        if new_score > THRESHOLD:
                            print("new pass!")
                            re_ocr_success.append(record) #to be added to Confrimed
                            second_round_pass_counter += 1
                            second_round_pass.append(record)
                        elif new_score < THRESHOLD:
                            second_round_fail_counter += 1 #to be manually reviewed
                            second_round_fail.append(record)
                    else:
                        print("not in there")
                        not_in_there += 1
            elif len(match.keys()) <= 2:
                no_title_page.append(record) #<---- Sent to no_title_work.ipynb script
                no_title_page_identified += 1
    elif record[1] not in tpg_ids:
        lost_counter += 1




#print(fail_counter)

# print("fuzz_test example:", fuzz.partial_ratio("American history,", "\nI LLU STRATED\nWITIH NUMEROUS MAPS AND ENGRAVINGS.\nREVO)iT oiI     THO E c[ ) GLO)N IES.\nN~~~~ )2~or~~~:.\n2l\n~odu; o    &inc\n\n\n\n"))
print(f'''
    For Threshold at {THRESHOLD}:
    ----
    no title page available = {no_title_page_identified}
    ----
    first round pass = {first_round_passed_counter}
    first rounf fail = {first_round_fail_counter}
    ----
    second round pass = {second_round_pass_counter}
    second round fail = {second_round_fail_counter}
    not in there = {not_in_there}
    ---
    Lost! (not in tpg ids) = {lost_counter}

''')
mu.write_csv("no_title_page_ids.csv", no_title_page)
mu.write_csv("fc_passed1.csv", passed_first)
mu.write_csv("fp_second_round_fail.csv", second_round_fail)
mu.write_csv("fp_second_round_pass.csv", second_round_pass)
print("done")




#I'm tweaking away at some of the code here to try to find what the best approach is here, and where perhaps the best Threshold might be.

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

# Third Round of Fuzz Results (using .lower(), but not .strip()):
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

#Notes:
# I'm realizing that using .strip() doesn't make a difference as I'm using the fuzz.partial_ration() function that uses substring, rather than full strings.
# Using .lower() seems to make it too permissive, giving higher scores for string that ought not match:
#
# Example:
# Metadata Title: American history,
# OCR content: '\nI LLU STRATED\nWITIH NUMEROUS MAPS AND ENGRAVINGS.\nREVO)iT oiI     THO E c[ ) GLO)N IES.\nN~~~~ )2~or~~~:.\n2l\n~odu; o    &inc\n\n\n\n'
#
# Fuzz Score: 41 when using .lower()
# The title is correct, but the OCR string really shouldn't be matching that highly with the Metadata string; they're fully different
#
#
#
# However, not using .lower() makes it awfully strict.
# 
# Example:
# Title:  Engineering precedents for steam machinery : embracing the performances of steamships, experiments with propelling instruments, condensers, boilers, etc., accompanied by analyses of the same ... /
# OCR content: "\nENGINEERING PRECEDENTS\nFOR\nSTEAM MACHINERY;\nEMBRACING THE\nPERFORMANCES OF STEAMSHIPS,\nEXPERIMENTS\nWITH\nPROPELLING INSTRUMENTS, CONDENSERS, BOILERS, ETC.,\nACCOMPANIED BY ANALYSES OF THE SAME;\nTHE WHOLE BEING ORIGINAL MATTER\nAND ARRANGED IN THE MOST PRACTICAL AND USEFUL MANNER\nFOR ENGINEERS.\nBY B. F. ISHERWOOD,\nCHIEF ENGINEER U. S. NAVY..\nN  E XW Y O  K:\nH. BAILLIPRE, 290 BROADWAY.\nLONDON: H. BAILLItRE, 219 REGENT STREET.\nPARIS: J. B. BAILLItRE ET FILS, RUE HAUTEFEUILLE.\nMADRID: C. BAILLY-BAILLItRE, CALLE DEL PRINCIPE.\n1858.\n\n\n\n",
#
# Score without .lower() = 16
# Score with .lower() = 92
#
#
# Fourth Round of Fuzz Results using process.extractOne() with processor=partial_ratio
#   - 100   : 1636
#   - 99-90 : 3792
#   - 89-80 : 1102
#   - 79-70 : 640
#   - 69-60 : 413
#   - 59-50 : 256
#   - 49-40 : 252
#   - 39-30 : 111
#   - 29-20 : 49
#   - 19-10 : 5
#   -  9-0  : 2
#
# I'm thinking maybe a threshold of 75?
#
#
#
# Fith Round of Fuzz Results using process.extractOne() with processor=token_sort_ratio
#   - 100   : 0
#   - 99-90 : 35
#   - 89-80 : 283
#   - 79-70 : 603
#   - 69-60 : 869
#   - 59-50 : 1115
#   - 49-40 : 1255
#   - 39-30 : 1370
#   - 29-20 : 1369
#   - 19-10 : 1002
#   -  9-0  : 294
#
#
# December 21, 2022:
# Implemented new version of bs_func.py to extract page OCRs; it lowered the number of items without title pages
# from 1810 to 384.
#