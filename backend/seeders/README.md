# Database Seeders

This folder contains database seeder scripts for populating initial data.

## Available Seeders

### 1. Category Seeder (`category_seeder.py`)

Seeds restaurant categories into the database.

**Categories included:**

-   Restoran Indonesia
-   Fast Food
-   Seafood Restaurant
-   Cafe & Coffee Shop
-   Bakery & Dessert
-   Asian Cuisine
-   Western Restaurant
-   Vegetarian Restaurant
-   Street Food
-   Fine Dining
-   Food Court
-   Warung Tradisional

### 2. Main Seeder (`run_seeders.py`)

Runs all seeders in the correct order.

## Usage

### Run Individual Seeders

```bash
# Seed categories only
cd backend/seeders
python category_seeder.py
```

### Run All Seeders

```bash
# Run all seeders in correct order
cd backend/seeders
python run_seeders.py
```

## Migration Scripts

Migration scripts are located in the main backend folder:

-   `migrate_restaurant_categories.py` - Migrates existing restaurants to use categories

```bash
# Run migration (after seeding categories)
cd backend
python migrate_restaurant_categories.py
```

## Important Notes

1. **Categories Seeder**: Will clear existing categories before seeding new ones
2. **Order**: Run seeders first, then migration scripts
3. **Virtual Environment**: Make sure to activate virtual environment before running
4. **Database**: Ensure database migrations are applied first

## Workflow

1. Apply database migrations: `flask db upgrade`
2. Run seeders: `cd seeders && python run_seeders.py`
3. Run migrations: `cd .. && python migrate_restaurant_categories.py`

## Folder Structure

```
seeders/
├── README.md                    # This file
├── category_seeder.py          # Restaurant categories seeder
├── run_seeders.py              # Main seeder runner
├── app/                        # App-specific seeders
├── data/                       # Seed data files
└── logs/                       # Seeder logs

backend/
├── migrate_restaurant_categories.py    # Migration script
└── ... (other files)
```
