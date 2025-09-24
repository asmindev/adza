#!/usr/bin/env python3
"""
Demo script untuk menunjukkan cara kerja sistem rating detail
"""


def demo_rating_calculation():
    """Demonstrasi perhitungan rating dari berbagai skenario"""

    print("🍜 DEMO SISTEM RATING DETAIL")
    print("=" * 50)

    scenarios = [
        {
            "name": "🍕 Pizza Mewah di Mall",
            "details": {
                "flavor": 5,  # Rasa enak banget
                "serving": 3,  # Porsi kecil
                "price": 2,  # Mahal
                "place": 5,  # Tempat bagus
            },
            "description": "Pizza enak tapi mahal dan porsi kecil",
        },
        {
            "name": "🍛 Nasi Padang Warung",
            "details": {
                "flavor": 4,  # Rasa enak
                "serving": 5,  # Porsi banyak
                "price": 5,  # Murah
                "place": 3,  # Tempat biasa
            },
            "description": "Enak, murah, banyak, tempat sederhana",
        },
        {
            "name": "🍝 Pasta Restoran Fancy",
            "details": {
                "flavor": 5,  # Rasa premium
                "serving": 4,  # Porsi pas
                "price": 3,  # Agak mahal
                "place": 5,  # Suasana mewah
            },
            "description": "Premium food dengan suasana mewah",
        },
        {
            "name": "🌮 Taco Street Food",
            "details": {
                "flavor": 4,  # Rasa oke
                "serving": 3,  # Porsi kecil
                "price": 4,  # Harga wajar
                "place": 2,  # Di pinggir jalan
            },
            "description": "Street food dengan rasa oke",
        },
        {
            "name": "🍜 Ramen Premium",
            "details": {
                "flavor": 5,  # Rasa perfect
                "serving": 4,  # Porsi cukup
                "price": 4,  # Worth it
                "place": 4,  # Cozy
            },
            "description": "Ramen berkualitas dengan harga reasonable",
        },
    ]

    print("\n📊 HASIL RATING BERDASARKAN KRITERIA:")
    print("-" * 70)

    for i, scenario in enumerate(scenarios, 1):
        details = scenario["details"]

        # Hitung rata-rata
        total = sum(details.values())
        average = round(total / len(details), 2)

        print(f"\n{i}. {scenario['name']}")
        print(f"   📝 {scenario['description']}")
        print(f"   🍽️  Rasa (flavor): {details['flavor']}/5")
        print(f"   🥄 Porsi (serving): {details['serving']}/5")
        print(f"   💰 Harga (price): {details['price']}/5")
        print(f"   🏪 Tempat (place): {details['place']}/5")
        print(f"   ⭐ RATING AKHIR: {average}/5")

        # Tambahkan interpretasi
        if average >= 4.5:
            print(f"   🎉 Excellent choice!")
        elif average >= 4.0:
            print(f"   👍 Good choice!")
        elif average >= 3.0:
            print(f"   🤔 Decent option")
        else:
            print(f"   🤷 Might want to reconsider")

    print("\n" + "=" * 50)
    print("💡 INSIGHT:")
    print("- Rating akhir = (flavor + serving + price + place) / 4")
    print("- Setiap kriteria memiliki bobot yang sama")
    print("- User bisa memberikan feedback spesifik per aspek")
    print("- Restaurant bisa tahu aspek mana yang perlu diperbaiki")


def demo_api_payload():
    """Contoh payload untuk API call"""

    print("\n🔌 CONTOH API PAYLOAD:")
    print("-" * 30)

    payloads = [
        {
            "description": "Rating untuk makanan enak tapi mahal",
            "payload": {
                "food_id": "12345-food-uuid",
                "rating_details": {"flavor": 5, "serving": 4, "price": 2, "place": 4},
            },
        },
        {
            "description": "Rating untuk warteg enak murah",
            "payload": {
                "food_id": "67890-food-uuid",
                "rating_details": {"flavor": 4, "serving": 5, "price": 5, "place": 3},
            },
        },
    ]

    for i, example in enumerate(payloads, 1):
        print(f"\n{i}. {example['description']}")
        print("   Payload JSON:")
        import json

        print("   " + json.dumps(example["payload"], indent=6))

        # Hitung expected result
        details = example["payload"]["rating_details"]
        expected_rating = sum(details.values()) / len(details)
        print(f"   Expected rating: {expected_rating}")


def demo_curl_examples():
    """Contoh curl command untuk testing"""

    print("\n🌐 CONTOH CURL COMMANDS:")
    print("-" * 25)

    print("\n1. POST Rating (Create new):")
    print(
        """curl -X POST http://localhost:5000/api/ratings \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \\
  -d '{
    "food_id": "your-food-uuid",
    "rating_details": {
      "flavor": 5,
      "serving": 4,
      "price": 4,
      "place": 5
    }
  }'"""
    )

    print("\n2. PUT Rating (Update existing):")
    print(
        """curl -X PUT http://localhost:5000/api/ratings \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \\
  -d '{
    "food_id": "your-food-uuid",
    "rating_details": {
      "flavor": 4,
      "serving": 3,
      "price": 3,
      "place": 4
    }
  }'"""
    )

    print("\n3. GET Food Ratings:")
    print("""curl -X GET http://localhost:5000/api/foods/your-food-uuid/ratings""")


if __name__ == "__main__":
    demo_rating_calculation()
    demo_api_payload()
    demo_curl_examples()

    print("\n" + "=" * 50)
    print("🚀 SISTEM RATING DETAIL SIAP DIGUNAKAN!")
    print("- Database schema sudah di-update")
    print("- API endpoints sudah mendukung format baru")
    print("- Backward compatibility terjaga")
    print("- Validation rules sudah diterapkan")
    print("\nSilakan jalankan Flask app dan test API-nya! 🎉")
