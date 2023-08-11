from dateparser.search import search_dates

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
        