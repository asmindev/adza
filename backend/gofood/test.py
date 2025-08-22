from scraper import GoFoodScraper

a = GoFoodScraper("YOUR_LOCATION_BASE64")

a.setup()

if a.api:
    import json

    res = a.api.get_outlet_details(
        "https://gofood.co.id/en/kendari/restaurant/mixue-ahmad-yani-kendari-kec-wua-wua-d39c7812-c11e-424f-aada-b0af4e8759f8"
    )

    with open("outlet_details.json", "w") as f:
        json.dump(res, f, indent=4)
    if res:
        print("Outlet details fetched successfully")
        details = a.parser.parse_outlet_details(res)
        print(details)
