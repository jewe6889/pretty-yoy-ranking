# Pretty Year-Over-Year Ranking

A CLI tool to generate beautiful year-over-year ranking visualizations showing how rankings change between consecutive years.

![Year-over-year ranking visualization](ranking_v2.png)

## Features

- Beautiful year-over-year ranking visualizations
- Flow connections between rankings across years
- Previous year position indicators
- Custom data via JSON files
- Color-coding by categories
- Customizable titles and subtitles
- High-resolution output (300 DPI)
- Special indicators for items moving in/out of top rankings
- Dynamic data processing via custom Python code
- **Database/Insights view** — tabular output with statistical summary (no chart generated)
- **Filtering** — filter entries by category or rank range before visualizing or exporting
- **Sorting** — sort the tabular view or CSV export by rank, item, category, or value
- **CSV export** — export filtered and sorted data to a CSV file

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
python generate_ranking.py
```

### Common Options

```bash
# Custom output file
python generate_ranking.py -o my_visualization.png

# Custom title and subtitle
python generate_ranking.py -t "My Custom Title" -s "My custom subtitle goes here"

# Using custom data
python generate_ranking.py -d sample_data.json

# Set maximum entries to display (default is 10)
python generate_ranking.py --max-entries 15
```

### Database / Insights View

Use `--database` (or `--insights`) to print ranking data as a formatted table with statistical insights instead of generating a chart:

```bash
python generate_ranking.py --database
python generate_ranking.py --insights           # alias for --database
```

Example output:
```
+--------+--------+------------------------------+----------------------+------------+
| Year   | Rank   | Item                         | Category             | Value      |
+--------+--------+------------------------------+----------------------+------------+
| 2024   | 1      | USA                          | North America        | 32.0%      |
...

=== STATISTICAL INSIGHTS ===

  2024:
    Total entries : 20
    Avg value     : 5.08%
    ...

  Changes from 2024 to 2025:
    Biggest rise  : Taiwan (+7 ranks)
    Biggest drop  : Italy (-4 ranks)
    New entries   : New Zealand, China, Denmark
    Dropped       : Russia, Argentina, Netherlands
```

### Filtering

```bash
# Filter by category (comma-separated for multiple)
python generate_ranking.py --database --filter-category "Asia"
python generate_ranking.py --database --filter-category "Asia,Europe"

# Filter by rank range
python generate_ranking.py --database --filter-rank-min 1 --filter-rank-max 5

# Combine filters
python generate_ranking.py --database --filter-category "Asia" --filter-rank-max 10
```

Filters also apply when generating the chart visualization.

### Sorting

```bash
# Sort by value descending in database view
python generate_ranking.py --database --sort-by value --sort-order desc

# Sort by item name ascending (default sort order)
python generate_ranking.py --database --sort-by item
```

Available `--sort-by` values: `rank` (default), `item`, `category`, `value`, `percentage`.

### CSV Export

```bash
# Export all data to CSV
python generate_ranking.py --export-csv output.csv

# Export filtered and sorted data to CSV (also generates chart)
python generate_ranking.py --filter-category "Europe" --sort-by value --sort-order desc --export-csv europe.csv

# Export without generating chart
python generate_ranking.py --database --export-csv output.csv
```

## Data Format

The data should be provided in JSON format:

```json
{
  "2023": [
    {"rank": 1, "item": "Product A", "category": "Electronics", "percentage": 32.0},
    {"rank": 2, "item": "Product B", "category": "Software", "percentage": 18.0},
    {"rank": 3, "item": "Product C", "category": "Electronics", "percentage": 12.0},
    {"rank": 4, "item": "Product D", "category": "Services", "percentage": 10.0},
    {"rank": 5, "item": "Product E", "category": "Services", "percentage": 5.5},
    {"rank": 6, "item": "Product F", "category": "Software", "percentage": 4.8},
    {"rank": 20, "item": "Product T", "category": "Hardware", "percentage": 0.2}
  ],
  "2024": [
    {"rank": 1, "item": "Product B", "category": "Software", "percentage": 28.0},
    {"rank": 2, "item": "Product C", "category": "Electronics", "percentage": 22.0},
    {"rank": 3, "item": "Product A", "category": "Electronics", "percentage": 18.0},
    {"rank": 20, "item": "Product U", "category": "Services", "percentage": 0.4}
  ]
}
```

Each item requires these properties:
- `rank`: Position in the ranking
- `item`: Name of the item
- `category`: Category for color-coding
- `percentage`: Numeric value representing the item's share

> **Note**: Include data beyond the top 10 (up to rank 20 or more) to properly show items that moved in or out of the top rankings.

## License

This project is open-source. Feel free to use and modify as needed.
