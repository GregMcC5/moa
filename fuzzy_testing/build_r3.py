import metadata_utils as mu

fp_r2_fail = mu.read_csv("fp_second_round_fail.csv")
notpg_r2_fail = mu.read_csv("notpg_r2_failed.csv")

r3 = fp_r2_fail + notpg_r2_fail

for entry in r3:
    url = f"https://quod.lib.umich.edu/m/moa/{entry[1]}/"
    entry.insert(0, url)
    entry.insert(0, None)

r3.insert(0, ["confirm?", "link", "mms_id", "dlxs_id", "author", "title", "pub_date", "publisher", "pub_place", "language"])

mu.write_csv("round3_test.csv", r3)
print("done")