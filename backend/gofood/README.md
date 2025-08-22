# GoFood Scraper - Clean & Minimal

Struktur kode yang telah direorganisasi untuk menjadi lebih minimalis dan terorganisir.

## Struktur Folder Baru

```
gofood/
├── __init__.py                 # Main exports
├── main.py                     # Entry point sederhana
├── scraper.py                  # Main scraper (clean)
├── README.md                   # Documentation
│
├── core/                       # Core models & data structures
│   ├── __init__.py
│   └── models.py               # Dataclass models
│
├── services/                   # Business logic services
│   ├── __init__.py
│   ├── api_client.py          # HTTP API client
│   └── parser.py              # Data parsing service
│
├── utils/                      # Utilities & helpers
│   ├── __init__.py
│   ├── cookies.py             # Cookie management
│   ├── excel_export.py        # Excel export utility
│   └── helpers.py             # Helper functions
│
├── config/                     # Configuration & settings
│   ├── __init__.py
│   ├── settings.py            # App settings & paths
│   └── cookies.json           # Authentication cookies
│
├── logs/                       # Log files
│   └── gofood_scraper.log     # Application logs
│
└── output/                     # Export output files
    └── *.xlsx                 # Excel export files
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
