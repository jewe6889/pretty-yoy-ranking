# Pretty Year-Over-Year Ranking

A CLI tool to generate beautiful year-over-year ranking visualizations, perfect for showing how rankings change between consecutive years. The visualization includes flow connections between years and indicators for previous year rankings.

## Features

- Generate beautiful year-over-year ranking visualizations
- Show connections between rankings across consecutive years
- Include indicators for previous year positions
- Support for custom data via JSON files
- Color-coding by categories/regions
- Customizable titles and subtitles
- High-resolution output (300 DPI)
- Special indicators for items that moved out of top rankings
- "NEW" indicators for items that moved into top rankings

## Installation

This tool requires Python 3.6+ and the following dependencies:
- matplotlib
- numpy
- pandas

Install the dependencies with:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Generate a visualization using the built-in sample data:

```bash
python generate_ranking.py
```

This will create a file named `ranking_v2.png` in the current directory.

### Custom Output File

```bash
python generate_ranking.py -o my_visualization.png
```

### Custom Title and Subtitle

```bash
python generate_ranking.py -t "My Custom Title" -s "My custom subtitle goes here"
```

### Using Custom Data

Prepare a JSON file with your data (see `sample_data.json` for the format), then run:

```bash
python generate_ranking.py -d sample_data.json
```

### Using the Shell Script (Linux/Mac)

For convenience, you can also use the provided shell script:

```bash
chmod +x generate_chart.sh  # Make executable (first time only)
./generate_chart.sh -o custom_output.png
```

## Data Format

The data should be provided in JSON format with the following structure:

```json
{
  "2023": [
    {"rank": 1, "country": "USA", "region": "North America", "percentage": 32.0},
    {"rank": 2, "country": "Japan", "region": "Asia", "percentage": 18.0},
    {"rank": 3, "country": "South Korea", "region": "Asia", "percentage": 12.0},
    {"rank": 4, "country": "UK", "region": "Europe", "percentage": 10.0},
    {"rank": 5, "country": "France", "region": "Europe", "percentage": 5.5},
    {"rank": 6, "country": "India", "region": "Asia", "percentage": 4.8},
    ...
    {"rank": 20, "country": "Nigeria", "region": "Africa", "percentage": 0.2}
  ],
  "2024": [
    {"rank": 1, "country": "Japan", "region": "Asia", "percentage": 28.0},
    {"rank": 2, "country": "South Korea", "region": "Asia", "percentage": 22.0},
    {"rank": 3, "country": "USA", "region": "North America", "percentage": 18.0},
    ...
    {"rank": 20, "country": "Denmark", "region": "Europe", "percentage": 0.4}
  ]
}
```

Each year should have a list of items with the following properties:
- `rank`: The position in the ranking (1-20 or more)
- `country`: The name of the item (can be any string, doesn't have to be a country)
- `region`: The category for color-coding (used for visual grouping)
- `percentage`: A numeric value representing the item's share/percentage

> **Note**: Include data beyond the top 10 (up to rank 20 or more) to properly show items that moved in or out of the top rankings.

## Example Output

The visualization will show:

![Year-over-year ranking visualization](ranking_v2.png)

Key features of the visualization:
- Left column: Previous year rankings (e.g., 2023)
- Right column: Current year rankings (e.g., 2024)
- Flow connections showing movement between years
- Rank change indicators (+1, -2, etc.) on connection lines
- "NEW" indicators for items that entered the top 10
- Special indicators for items that dropped out of top 10
- Color-coding based on region/category
- Percentage values for each item

## Customization

The visualization has several customization options:
- Colors for different regions/categories
- Line thickness based on percentage values
- Custom titles and subtitles
- Output file format and resolution

To modify these, edit the constants at the beginning of the `generate_ranking.py` file.

## License

This project is open-source. Feel free to use and modify as needed.
