import requests
import csv
import os
from datetime import datetime

API_KEY = os.getenv("AMADEUS_API_KEY")
API_SECRET = os.getenv("AMADEUS_API_SECRET")
BASE_URL = "https://api.amadeus.com"

ORIGIN_CITIES = ["VNO", "LHR", "WAW", "CDG"]
DESTINATION = "ISB"
DEPARTURE_DATE = "2025-09-04"
CSV_FILE = "islamabad_flight_prices.csv"

def get_access_token():
    if not API_KEY or not API_SECRET:
        print("❌ API raktai nepateikti")
        return None

    response = requests.post(
        f"{BASE_URL}/v1/security/oauth2/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "client_credentials",
            "client_id": API_KEY,
            "client_secret": API_SECRET
        }
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print("❌ Token klaida:", response.status_code, response.text)
        return None

def search_flights(access_token, origin):
    url = f"{BASE_URL}/v2/shopping/flight-offers"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {
        "originLocationCode": origin,
        "destinationLocationCode": DESTINATION,
        "departureDate": DEPARTURE_DATE,
        "adults": 1,
        "max": 3
    }

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return [
            {
                "date_checked": datetime.utcnow().strftime("%Y-%m-%d"),
                "origin": origin,
                "destination": DESTINATION,
                "departure_date": DEPARTURE_DATE,
                "airline": f.get("validatingAirlineCodes", ["N/A"])[0],
                "price_EUR": f["price"]["total"]
            }
            for f in response.json().get("data", [])
        ]
    else:
        print(f"❌ Klaida {origin}: {response.status_code}")
        return []

def save_to_csv(data):
    file_exists = os.path.exists(CSV_FILE)
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        if not file_exists:
            writer.writeheader()
        writer.writerows(data)

if __name__ == "__main__":
    print("🚀 Paleidimas...")
    token = get_access_token()
    if token:
        all_data = []
        for origin in ORIGIN_CITIES:
            offers = search_flights(token, origin)
            all_data.extend(offers)
        if all_data:
            save_to_csv(all_data)
            print("✅ Skrydžiai išsaugoti!")
        else:
            print("⚠️ Nerasta jokių pasiūlymų")
