import metadata_utils as mu

passed = mu.read_csv("passed.csv")

with open("ALMA_stubs.txt", 'r') as f:
    lines = f.readlines()
f.close

passed_stubs = []

for line in lines:
    id = line.split(" ")[0]
    if id in [x[0] for x in passed]:
        passed_stubs.append([x for x in passed if x[0] == id][0])

mu.write_csv("passed_stubs.csv", passed_stubs)