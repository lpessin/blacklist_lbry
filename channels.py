import requests
import csv

# Get channels names and them their IDs. Channels names from top 200 (lbrynomics). Will be automated soon.

names = []
with open('channels', 'r') as r:
    reader = csv.reader(r)
    for row in reader:
        names.append(row[0])

claim_ids = []
for name in names:
    url = f'lbry://{name}'
    call = requests.post("http://localhost:5279", json={"method": "resolve",
                                                        "params": {"urls": [url]}}).json().get('result').get(url)
    id = call.get('claim_id')
    claim_ids.append(id)

print(claim_ids)
print(len(claim_ids))

with open('ids', 'w', newline='') as ids:
    write = csv.writer(ids)
    for i in claim_ids:
        write.writerow([i])
