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

## Installation

This tool requires Python 3.6+ and the following dependencies:
- matplotlib
- numpy
- pandas

Install the dependencies with:

```bash
pip install matplotlib numpy pandas
```

## Usage

### Basic Usage

Generate a visualization using the built-in sample data:

```bash
python generate_ranking.py
```

This will create a file named `movie_countries_ranking.png` in the current directory.

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

## Data Format

The data should be provided in JSON format with the following structure:

```json
{
  "2022": [
    {"rank": 1, "country": "USA", "region": "North America", "percentage": 45.0},
    ...
  ],
  "2023": [
    ...
  ],
  "2024": [
    ...
  ]
}
```

Each year should have a list of items with the following properties:
- `rank`: The position in the ranking (1-10)
- `country`: The name of the item (can be any string)
- `region`: The category for color-coding
- `percentage`: A numeric value representing the item's share/percentage

## Example Output

The visualization will show:
- Left column: Previous year rankings (e.g., 2023)
- Right column: Current year rankings (e.g., 2024)
- Flow connections showing movement between years
- Small indicators showing the position from two years ago (e.g., 2022)
- Color-coding based on region/category
- Percentage values for each item

## License

This project is open-source. Feel free to use and modify as needed.
