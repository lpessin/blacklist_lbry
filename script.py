import requests
import datetime
from datetime import datetime, timedelta
import xlsxwriter
import csv

# Search for comments on claims from a list of channels. Better chances to catch spam on top channels.
CHANNEL_IDS = []
with open('ids', 'r') as r:
    reader = csv.reader(r)
    for row in reader:
        CHANNEL_IDS.append(row[0])

# Filter comments from a list of Keywords and sentences
KEYWORDS = ['follow me', 'support each other', 'follow you back', 'follow my channel', "i'll follow you",
            'puedes seguirme', 'watch me', 'get free money', 'earn free bitcoin', 'follow for follow']

DAYS_BACK = 15

# Create CSV file
CSV_FILE = True

# Create XLSX file
XLSX_FILE = True


def get_claim_ids():
    claim_ids = []
    limit = datetime.now() - timedelta(days=DAYS_BACK)
    timestamp_limit = str(int(datetime.timestamp(limit)))
    for page in range(1, 30):
        call = requests.post("http://localhost:5279", json={"method": "claim_search", "params": {
            "claim_ids": [],
            "channel_ids": CHANNEL_IDS,
            'release_time': f'>{timestamp_limit}',
            "not_channel_ids": [],
            "stream_types": [],
            "media_types": [],
            "any_tags": [],
            "all_tags": [],
            "not_tags": [],
            "any_languages": [],
            "all_languages": [],
            "not_languages": [],
            "any_locations": [],
            "all_locations": [],
            "not_locations": [],
            "order_by": [],
            "page_size": 50,
            "page": page,
            'no_totals': True,
            }}).json().get('result').get('items')
        for claim in call:
            claim_id = claim.get('claim_id')
            claim_ids.append(claim_id)
    print(f'Searching spam on {len(claim_ids)} claims...%')
    return claim_ids


def get_spam_comments(claim_ids):
    keywords = KEYWORDS
    spam_list = []
    for claim_id in claim_ids:
        call = requests.post("http://localhost:5279", json={"method": "comment_list", "params": {
            "claim_id": claim_id,
            "include_replies": False, }}).json().get('result').get('items')
        for comment in call:
            content = comment.get('comment').lower()
            for keyword in keywords:
                if keyword in content:
                    spam_list.append([comment.get('timestamp'), comment.get('comment_id'), comment.get('claim_id'),
                                      comment.get('channel_name'), content])
    print(f'{len(spam_list)} spam comments found!')
    return spam_list


# Start
print('Searching...%')
claim_ids = get_claim_ids()
data = get_spam_comments(claim_ids)

# Print result
print(data)

# timestamp - days back
timestamp = f'{str(int(datetime.timestamp(datetime.now())))}-{str(DAYS_BACK)}'

# Create xlsx file
if XLSX_FILE:
    print('Building xlsx...%')
    workbook = xlsxwriter.Workbook(f'lists/{timestamp}.xlsx')
    worksheet = workbook.add_worksheet('data')
    worksheet.write(0, 0, f'Created on {datetime.now()}')
    worksheet.write(1, 0, f'Days back {DAYS_BACK} - Claims: {len(claim_ids)} - Comments found: {len(data)}')
    worksheet.write(2, 0, 'https://github.com/lpessin/spamlist_lbry')
    worksheet.add_table(f'A4:E{len(data) + 4}', {'columns': [{'header': 'Timestamp'},
                                                         {'header': 'Comment_ID'},
                                                         {'header': 'Claim_ID'},
                                                         {'header': 'Channel'},
                                                         {'header': 'Comment'}]})
    row = 4
    col = 0
    for item in data:
        worksheet.write(row, col, f'{datetime.fromtimestamp(item[0])}')
        worksheet.write(row, col + 1, item[1])
        worksheet.write(row, col + 2, item[2])
        worksheet.write_url(row, col + 3, f"https://lbry.tv/{item[3]}", string=item[3])
        worksheet.write(row, col + 4, item[4])
        row += 1
    workbook.close()
    print(f'{timestamp}.xlsx created')

'''
encode issues
# Create CSV file
if CSV_FILE:
    with open(f'{timestamp}', 'w', newline="") as c:
        writer = csv.writer(c)
        for item in data:
            writer.writerow([item])
    print('CSV CREATED')'''
