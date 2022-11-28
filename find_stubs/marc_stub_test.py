import pymarc
import metadata_utils as mu

stubs = []
fulls = []
with open("full_moa_export.mrc", 'rb') as data:
    reader = pymarc.MARCReader(data)
    for record in reader:
        if str(record["001"])[6:] == "99187365819206381":
            print("stub", len([thing for thing in record]))
            print(record.title())
        if str(record["001"])[6:] == "990003184960106381":
            print("full", len([thing for thing in record]))

        if len([x for x in record]) < 15:  #<--subject to discussion
            print(record["001"])
            stubs.append([str(record["001"])[6:], len([thing for thing in record])])
        else:
            fulls.append([str(record["001"])[6:], len([thing for thing in record])])

print(f'''
    stubs = {len(stubs)}
    fulls = {len(fulls)}
''')


alma_stubs = open("ALMA_stubs.txt", 'w')
for entry in stubs:
    print(entry[0], entry[1], file=alma_stubs)
alma_stubs.close
