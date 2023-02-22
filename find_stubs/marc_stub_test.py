import pymarc
import metadata_utils as mu

confirmed = mu.read_csv("confirmed.csv")

stubs = []
fulls = []


marc_field_data = []

with open("full_moa_export.mrc", 'rb') as data:
    reader = pymarc.MARCReader(data)
    for record in reader:
        marc_field_data.append([str(record["001"][6:]), len([x for x in record])])

        # if str(record["001"])[6:] == "99187366606806381":
        #     print("stub", len([thing for thing in record]))
        #     print(record.title())
        # if str(record["001"])[6:] == "990003184960106381":
        #     print("full", len([thing for thing in record]))

        # if len([x for x in record]) == 9:  #<--subject to discussion
        #     print(record["001"])
        #     stubs.append([str(record["001"])[6:], len([thing for thing in record])])
        # else:
        #     fulls.append([str(record["001"])[6:], len([thing for thing in record])])

for entry in confirmed[1:]:
    print("looking...")
    if entry[0] in [x[0] for x in marc_field_data]:
        print("found it")
        match = [x for x in marc_field_data if x[0] == entry[0]][0]
        print(match[1])
        if match[1] <= 10:
            print("found stub")

print(f'''
    stubs = {len(stubs)}
    fulls = {len(fulls)}
''')


alma_stubs = open("ALMA_stubs.txt", 'w')
for entry in stubs:
    print(entry[0], entry[1], file=alma_stubs)
alma_stubs.close
