import requests
import datetime
from datetime import datetime, timedelta
import xlsxwriter

# Search for comments on claims from a list of channels. Better chances to catch spam on top channels.
CHANNEL_IDS = ['3fda836a92faaceedfe398225fb9b2ee2ed1f01a', 'cda9c4e92f19d6fe0764524a2012056e06ca2055',
               '4c29f8b013adea4d5cca1861fb2161d5089613ea', '36b7bd81c1f975878da8cfe2960ed819a1c85bb5',
               'f8219d5914b95a0a2f670d92dea5dc24133278e9', 'f3da2196b5151570d980b34d311ee0973225a68e',
               '0f3a709eac3c531a68c97c7a48b2e37a532edb03', '4ad942982e43326c7700b1b6443049b3cfd82161',
               '56e86eb938c0b93beccde0fbaaead65755139a10', '5bd299a92e7b31865d2bb3e2313402edaca41a94',
               'fb364ef587872515f545a5b4b3182b58073f230f', 'c9da929d12afe6066acc89eb044b552f0d63782a',
               'e8f68563d242f6ac9784dcbc41dd86c28a9391d6', '4651d91cc32c01243069af1f39468928102750dc',
               'feb61536c007cdf4faeeaab4876cb397feaf6b51', '828174a6adcdeee74de5211db1d006716aa54d07',
               'e11e2fc3056137948d2cc83fb5ca2ce9b57025ec', 'f399d873e0c37cf24de9569b5f22bbb30a5c6709',
               '4ee7cfaf1fc50a6df858ed0b99c278d633bccca9', '74333143a3dcc001a5602aa524583fc75a013d75']

# Filter comments from a list of Keywords and sentences
KEYWORDS = ['follow me', 'support each other', 'follow you back', 'follow my channel', "i'll follow you",
            'puedes seguirme', 'watch me', 'get free money', 'earn free bitcoin', 'follow for follow']


DAYS_BACK = 15


def get_claim_ids():
    claim_ids = []
    limit = datetime.now() - timedelta(days=DAYS_BACK)  # days back to search
    timestamp_limit = str(int(datetime.timestamp(limit)))
    for page in range(1, 30):
        call = requests.post("http://localhost:5279", json={"method": "claim_search", "params": {
            "claim_ids": [],
            # 20 of the top channels to get claims from:
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
            "page": page
            }}).json().get('result').get('items')
        for claim in call:
            claim_id = claim.get('claim_id')
            claim_ids.append(claim_id)
    print(f'Searching spam on {len(claim_ids)} claims...%')
    return claim_ids


def get_spam_comments(claim_ids):
    keywords = KEYWORDS
    blacklist = []
    spam_count = 0
    for claim_id in claim_ids:
        call = requests.post("http://localhost:5279", json={"method": "comment_list", "params": {
            "claim_id": claim_id,
            "include_replies": False, }}).json().get('result').get('items')
        for comment in call:
            content = comment.get('comment').lower()
            for keyword in keywords:
                if keyword in content:
                    spam_count += 1
                    blacklist.append([comment.get('comment_id'), comment.get('claim_id'),
                                      comment.get('channel_name'), content])
    print(f'{spam_count} spam comments found!')
    return blacklist

# Start
claim_ids = get_claim_ids()
blacklist = get_spam_comments(claim_ids)
# Print result
print(blacklist)
# Create xlsx file
workbook = xlsxwriter.Workbook(f'{str(int(datetime.timestamp(datetime.now())))}-{str(DAYS_BACK)}.xlsx')
worksheet = workbook.add_worksheet()
row = 0
col = 0
for item in blacklist:
    worksheet.write(row, col, item[0])
    worksheet.write(row, col + 1, item[1])
    worksheet.write(row, col + 2, item[2])
    worksheet.write(row, col + 3, item[3])
    row += 1
workbook.close()
print(f'{str(int(datetime.timestamp(datetime.now())))}-{str(DAYS_BACK)}.xlsx created')
