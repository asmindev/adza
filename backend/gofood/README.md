# GoFood Scraper - Clean & Minimal

Struktur kode yang telah direorganisasi untuk menjadi lebih minimalis dan terorganisir.

## Struktur Folder Baru

# GoFood Scraper & Database Importer

Tool untuk scraping data GoFood dan mengimpor ke database aplikasi ADZA.

## File Structure

```
gofood/
├── main.py                 # Entry point utama dengan argumen CLI
├── import_to_db.py         # Module untuk import ke database
├── scraper.py              # Module scraper GoFood
├── output/                 # Folder hasil scraping Excel
│   ├── gofood_detailed_*.xlsx
│   └── gofood_outlets_*.xlsx
└── config/
    └── cookies.json        # Cookies untuk autentikasi
```

## Usage

### 1. Mode Scraping (Default)

Scraping data dari GoFood API:

```bash
python main.py --location YOUR_LOCATION_BASE64 --max-pages 5 --max-details 10
```

### 2. Mode Import Database

Import data Excel ke database:

```bash
# Import file terbaru otomatis
python main.py --db

# Import file Excel spesifik
python main.py --db --file output/gofood_detailed_20250825_181340.xlsx

# Preview data tanpa import
python main.py --preview
python main.py --preview --file output/gofood_detailed_20250825_181340.xlsx
```

### 3. Command Line Arguments

| Argument           | Description                           | Default                |
| ------------------ | ------------------------------------- | ---------------------- |
| `--db`             | Mode import ke database               | False                  |
| `--file`, `-f`     | File Excel spesifik untuk import      | Latest file            |
| `--preview`, `-p`  | Preview data tanpa import             | False                  |
| `--location`, `-l` | Location base64 untuk scraping        | "YOUR_LOCATION_BASE64" |
| `--max-pages`      | Maksimal halaman untuk scraping       | 5                      |
| `--max-details`    | Maksimal outlet untuk detail scraping | 10                     |

## Database Schema

### Restaurants Table

-   `id` (String, PK)
-   `name` (String, required)
-   `description` (Text)
-   `address` (String, required)
-   `phone` (String)
-   `email` (String)
-   `latitude` (Float, required)
-   `longitude` (Float, required)
-   `rating_average` (Float, default: 0.0)
-   `is_active` (Boolean, default: True)
-   `created_at`, `updated_at`

### Foods Table

-   `id` (String, PK)
-   `name` (String, required)
-   `description` (Text)
-   `category` (String)
-   `price` (Float)
-   `restaurant_id` (String, FK)
-   `created_at`, `updated_at`

### Food Images Table

-   `id` (String, PK)
-   `food_id` (String, FK)
-   `image_url` (String)
-   `is_main` (Boolean)
-   `filename` (String)

## Import Process

1. **Load Excel Data**: Baca file Excel dengan sheet "Outlets" dan "Foods"
2. **Process Restaurants**:
    - Buat atau cari restaurant berdasarkan nama, latitude, longitude
    - Map UID ke restaurant ID untuk relasi foods
3. **Process Foods**:
    - Buat food untuk setiap restaurant
    - Tambahkan image jika tersedia
    - Skip jika food sudah ada

## Data Mapping

### From Excel to Database

**Outlets Sheet → Restaurants Table:**

-   `Name` → `name`
-   `Tags` → `description` (formatted as "Categories: {tags}")
-   `Latitude`, `Longitude` → `latitude`, `longitude`
-   `Average Rating` → `rating_average`
-   Default: `address` = "Kendari, Sulawesi Tenggara"

**Foods Sheet → Foods Table:**

-   `Food Name` → `name`
-   `Description` → `description`
-   `Price` → `price` (converted from IDR)
-   `Restaurant UID` → mapped to `restaurant_id`
-   `Image URL` → FoodImage table

## Example Output

```bash
$ python main.py --db

🗄️  Database import mode
Starting import from: output/gofood_detailed_20250825_181340.xlsx
Loaded Excel file: output/gofood_detailed_20250825_181340.xlsx
Available sheets: ['Outlets', 'Foods']

Processing 10 restaurants...
Created new restaurant: RM Glatik, Kambu
Created new restaurant: Kopi Goffee, Wowawanggu
...

Processing 772 foods...
Created food: Nasi Campur - 54000.0
Created food: Nyuk Nyang (umum) - 34000.0
...

✅ Import completed successfully!
📍 Restaurants created: 10
🍽️  Foods created: 772
```

## Requirements

-   Python 3.11+
-   Virtual environment aktif: `source ../backend/.venv/bin/activate`
-   Dependencies: pandas, openpyxl, Flask, SQLAlchemy
-   Database connection ke backend ADZA

## Error Handling

-   **File not found**: Otomatis cari file terbaru di folder output
-   **Duplicate data**: Skip data yang sudah ada
-   **Invalid data**: Convert dengan safe defaults
-   **Database errors**: Rollback transaksi

## Notes

-   Import adalah **incremental** - data existing tidak akan ditimpa
-   Restaurant diidentifikasi berdasarkan `name`, `latitude`, `longitude`
-   Food diidentifikasi berdasarkan `name` dan `restaurant_id`
-   Semua price dalam IDR, disimpan sebagai float
-   Image URL disimpan di table terpisah `food_images`

## Original Scraper Structure

```
gofood/
├── core/                       # Core models & data structures
│   ├── __init__.py
│   └── models.py               # Dataclass models
├── services/                   # Business logic services
│   ├── __init__.py
│   ├── api_client.py          # HTTP API client
│   └── parser.py              # Data parsing service
├── utils/                      # Utilities & helpers
│   ├── __init__.py
│   ├── cookies.py             # Cookie management
│   ├── excel_export.py        # Excel export utility
│   └── helpers.py             # Helper functions
└── config/                     # Configuration & settings
    ├── __init__.py
    ├── settings.py            # App settings & paths
    └── cookies.json           # Authentication cookies
```

## Penggunaan Sederhana

```python
from gofood import GoFoodScraper

# Inisialisasi
scraper = GoFoodScraper(location="YOUR_LOCATION")

# Setup (load cookies, dll)
if scraper.setup():
    # Scrape outlets
    result = scraper.scrape_outlets(max_pages=5)
    print(f"Found {result.total_count} outlets")

    # Scrape detail (opsional)
    details = scraper.scrape_outlet_details(result.outlets[:10])
    filename = scraper.export_detailed_data(details)
```

## Perubahan Utama

### 1. **Struktur Folder Terorganisir**

-   `core/`: Models & data structures
-   `services/`: Business logic (API, parsing)
-   `utils/`: Utilities (cookies, export, helpers)
-   `config/`: Configuration management

### 2. **Kode Lebih Minimalis**

-   Fungsi dipecah sesuai tanggung jawab
-   Duplikasi kode dihilangkan
-   Import statements lebih bersih

### 3. **Dataclass Tetap Digunakan**

-   Semua model tetap menggunakan `@dataclass`
-   Struktur data tidak berubah
-   Export format tetap sama

### 4. **API Lebih Sederhana**

-   Main scraper class lebih clean
-   Method names lebih jelas
-   Error handling yang baik

### 5. **Configuration Centralized**

-   Semua config di satu tempat
-   Headers dan URLs terpusat
-   Mudah untuk maintenance

## Nilai Export/Save Tetap Sama

Data yang disimpan/export tetap sama dengan versi sebelumnya:

-   Format Excel tetap sama
-   Field-field data tidak berubah
-   Struktur output konsisten

## Migration dari Versi Lama

Untuk menggunakan versi baru, cukup ganti import:

```python
# Lama
from gofood.scraper import GoFoodScraper

# Baru
from gofood import GoFoodScraper
```

API usage tetap hampir sama, hanya lebih sederhana dan bersih.
