from dateparser.search import search_dates
from fuzzywuzzy import process, fuzz
import difflib
import requests


def fetch_fda_db():
    meds = set()
    for tag in ["Prescription", "Over-the-counter"]:
        limit, skip = 400, 0
        while True:
            print(tag, skip)
            result = requests.get(
                "https://api.fda.gov/drug/drugsfda.json",
                params={
                    "limit": limit,
                    "skip": skip,
                    "search": f'products.marketing_status:"{tag}"',
                },
            )
            result.raise_for_status()
            result = result.json()
            for res in result["results"]:
                for product in res["products"]:
                    meds.add(product["brand_name"])
                    for ingredient in product["active_ingredients"]:
                        if "strength" in ingredient:
                            if (idx := ingredient["strength"].find(" **")) != -1:
                                ingredient["strength"] = ingredient["strength"][:idx]
                            meds.add(f'{ingredient["name"]} {ingredient["strength"]}')
                            meds.add(
                                f'{product["brand_name"]} {ingredient["strength"]}'
                            )
                        else:
                            meds.add(ingredient["name"])
            if skip + limit >= result["meta"]["results"]["total"]:
                break
            skip += limit
    meds = sorted(meds, key=lambda x: x.lower())
    with open("meds.txt", "w") as f:
        f.write("\n".join(meds))
        f.write("\n")


def similarity_score(chunk, bigString):
    # return max([difflib.SequenceMatcher(None, chunk, string.upper()).ratio() for string in bigString])
    return max(
        [
            difflib.SequenceMatcher(
                None, chunk, bigString[i : i + len(chunk)].upper()
            ).quick_ratio()
            for i in range(len(bigString) - len(chunk) + 1)
        ]
    )


# Function to find the top matching drugs
def find_top_matching_drugs(drug_list, ocr_output, top_n=3):
    top_matches = []

    for drug in drug_list:
        # match_scores = process.extract(drug, ocr_output, scorer=fuzz.partial_ratio)
        # best_match = max(match_scores, key=lambda x: x[1])
        best_match = fuzz.partial_ratio(drug, ocr_output.upper())

        # if best_match[1] >= 80:  # You can adjust the threshold as needed
        if best_match >= 10:  # You can adjust the threshold as needed
            # top_matches.append((drug, best_match[1]))
            top_matches.append((drug, best_match))

    top_matches.sort(key=lambda x: x[1], reverse=True)
    # return top_matches[:top_n]
    return top_matches


def load_fda_db():
    with open("meds.txt", "r") as f:
        return f.read().split("\n")


def parse_meds(ocr_text, meds=load_fda_db()):
    print("Got meds")
    scores = list(map(lambda med: (med, similarity_score(med, ocr_text)), meds))
    print("Got scores")
    scores.sort(key=lambda x: x[1], reverse=True)
    print(scores[:10])


def parse_ocr(ocr_text):
    output = {"dateFilledDate": None, "refillDate": None, "expiryDate": None}
    dates = search_dates(ocr_text)
    dates.sort(key=lambda x: x[1])
    if len(dates) == 1:
        output["expiryDate"] = dates[0]
    elif len(dates) == 2:
        output["dateFilledDate"], output["expiryDate"] = dates
    elif len(dates) == 3:
        output["dateFilledDate"], output["refillDate"], output["expiryDate"] = dates
    else:
        output["dateFilledDate"], output["refillDate"], output["expiryDate"] = dates[:3]


ocr_output = [
    "* CVS pharmacy",
    "PSC 1578,",
    "Box 2410, APO AA 02400",
    "TEL 6365762933",
    "Rx 806146",
    "QTY: 90",
    "REFILLS: 6 by 11/16/2004",
    "PRSCBR: M. Braun",
    "DATE FILLED: 02/14/2004",
    "DISCARD AFTER: 11/16/2004",
    "RPH: K. Wang",
    "MFR: PharmaCore Solutions",
    "JULIA",
    "Julia",
    "Nature Made Vitamin D Lima",
    "7868 Larry Brooks Apt. 088, East Christinaside, NV",
    "97976",
    "Nature Made Vitamin D",
    "3",
    "MORNING",
    "MIDDAY",
    "Generic equivalent of: Lorem sed enim commodo",
    "Take 1 tablet once",
    "daily with food",
    "EVENING",
    "BEDTIME",
    "A PHARMACY ADVICE",
    "Important",
    "Information",
    "• Lorem ipsum dolor",
    "sit amet, consectetur",
    "adipiscing elit.",
    "• Sed do eiusmod",
    "tempor incididunt ut",
    "labore et dolore",
    "magna aliqua.",
    "• Ut enim ad minim",
    "veniam, quis nostrud",
    "exercitation ullamco",
    "laboris nisi ut aliquip",
    "ex ea commodo",
    "consequat.",
    "CAUTION Federal law prohibits the",
    "transter of this drag to any person",
    "other than the patient for whom it",
    "was prescribed.",
]
# ocr_output = [
#     "* CVS pharmacy",
#     "PSC 1578,",
#     "Box 2410, APO AA 02400",
#     "TEL 6365762933",
#     "Rx 463483",
#     "QTY: 30",
#     "REFILLS: 4 by 11/07/1989",
#     "PRSCBR: A. Singh",
#     "DATE FILLED: 07/17/1989",
#     "DISCARD AFTER: 01/17/1990",
#     "RPH: C. Wagner",
#     "MFR: VitaSolutions",
#     "Pharmaceuticals",
#     "VALENTINA",
#     "Prevacid",
#     "Valentina",
#     "Ferreira",
#     "747 Lowe Way, East Lisastad, FL 47665",
#     "Prevacid",
#     "MORNING",
#     "MIDDAY",
#     "Generic equivalent of: Lorem sed enim commodo",
#     "Take 1 capsule once a",
#     "day before breakfast",
#     "EVENING",
#     "BEDTIME",
#     "A PHARMACY ADVICE",
#     "Important",
#     "Information",
#     "• Lorem ipsum dolor",
#     "sit amet, consectetur",
#     "adipiscing elit.",
#     "• Sed do eiusmod",
#     "tempor incididunt ut",
#     "labore et dolore",
#     "magna aliqua.",
#     "• Ut enim ad minim",
#     "veniam, quis nostrud",
#     "exercitation ullamco",
#     "laboris nisi ut aliquip",
#     "ex ea commodo",
#     "consequat.",
#     "CAUTION Federal law prohibits the",
#     "transfer of this dnag to any person",
#     "other than the patient for whom it",
#     "was prescribed.",
# ]
comb = "\n".join(ocr_output)
db = load_fda_db()
# parse_meds(comb, db)

print(find_top_matching_drugs(db, comb))
