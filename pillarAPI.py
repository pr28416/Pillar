from dateparser.search import search_dates
import difflib
import requests

def fetch_fda_db():
    meds = set()
    for tag in ['Prescription', 'Over-the-counter']:
        limit, skip = 400, 0
        while True:
            print(tag, skip)
            result = requests.get(
                'https://api.fda.gov/drug/drugsfda.json',
                params={
                    'limit': limit,
                    'skip': skip,
                    'search': f'products.marketing_status:"{tag}"'
                }
            )
            result.raise_for_status()
            result = result.json()
            for res in result['results']:
                for product in res['products']:
                    meds.add(product['brand_name'])
                    for ingredient in product['active_ingredients']:
                        if "strength" in ingredient:
                            if (idx:=ingredient["strength"].find(" **")) != -1:
                                ingredient["strength"] = ingredient["strength"][:idx]
                            meds.add(f'{ingredient["name"]} {ingredient["strength"]}')
                            meds.add(f'{product["brand_name"]} {ingredient["strength"]}')
                        else:
                            meds.add(ingredient["name"])
            if skip + limit >= result['meta']['results']['total']:
                break
            skip += limit
    meds = sorted(meds, key=lambda x: x.lower())
    with open('meds.txt', 'w') as f:
        f.write('\n'.join(meds))
        f.write('\n')

def similarity_score(chunk, bigString):
    return max([difflib.SequenceMatcher(None, chunk, bigString[i:i+len(chunk)]).ratio() for i in range(len(bigString)-len(chunk)+1)])

def load_fda_db():
    with open('meds.txt', 'r') as f:
        return f.read().split('\n')
    
def parse_meds(ocr_text):
    meds = load_fda_db()
    scores = list(map(lambda med: (med, similarity_score(med, ocr_text)), meds))
    scores.sort(key=lambda x: x[1], reverse=True)
    print(scores[:3])

def parse_ocr(ocr_text):
    output = {
        'dateFilledDate': None,
        'refillDate': None,
        'expiryDate': None
    }
    dates = search_dates(ocr_text)
    dates.sort(key=lambda x: x[1])
    if len(dates) == 1:
        output['expiryDate'] = dates[0]
    elif len(dates) == 2:
        output['dateFilledDate'], output['expiryDate'] = dates
    elif len(dates) == 3:
        output['dateFilledDate'], output['refillDate'], output['expiryDate'] = dates
    else:
        output['dateFilledDate'], output['refillDate'], output['expiryDate'] = dates[:3]