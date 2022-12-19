import metadata_utils as mu
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import pytesseract as pyt
import os.path
import os

THRESHOLD = 75

tpg_content = mu.read_file("tpg_content_full.json") + mu.read_file("tpg_content_full2.json")
passed_records = mu.read_file("passed.csv")

fail_counter = 0

passed_first = []
full_paths = []
re_ocr_success = []

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
            if len(match.keys()) > 2:
                selection, score = process.extractOne(query=record[3],choices=[key + "||" + val for key, val in match.items() if "tpg" in key], scorer=fuzz.partial_ratio)
                page = selection.split("||")[0]
                ocr = selection.split("||")[1]
                # #-Doing some testing
                if record[1] == "AAF1187.1843.001":
                    print(f'''
                    score: {score}
                    title: {record[3]}
                    page : {page}
                    ocr : {ocr}
                    ''')
                # #-appending to a text file
                with open("fuzz_output.txt", 'a') as file:
                    file.write(f"{record[3]}\nfuzz score: {score}, title page index:? {page}\nid: {record[1]}\n\n")
                # #-checking score, appending
                # if score > THRESHOLD:
                #     passed_first.append(record)
                # elif score < THRESHOLD:
                #     fail_counter += 1
                    # #-write filenames
                    # root = record[1]
                    # path = f"/n1/obj/{root[0]}/{root[1]}/{root[2]}/{root}/{page.strip('tpg - ')}.tif"
                    # full_paths.append(path)
                    # #-check for filepath, do re-OCR
                    # img_files = os.listdir("moa_images")
                    # if path in img_files:
                    #     if process.extractOne(record[3],[pyt.image_to_string(path)], scorer=fuzz.partial_ratio)[1] > THRESHOLD:
                    #         re_ocr_success.append(record)
                    #     else:
                    #         print("still a problem")




#print(fail_counter)

# print("fuzz_test example:", fuzz.partial_ratio("American history,", "\nI LLU STRATED\nWITIH NUMEROUS MAPS AND ENGRAVINGS.\nREVO)iT oiI     THO E c[ ) GLO)N IES.\nN~~~~ )2~or~~~:.\n2l\n~odu; o    &inc\n\n\n\n"))

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
