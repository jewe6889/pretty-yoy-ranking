# Year-over-Year Ranking Visualization Project

## Requirements
- Create a CLI tool to generate a visualization similar to the ranking_template.jpeg
- Focus on countries of origin for movies seen in 2023 and 2024
- Show year-over-year changes in rankings
- Visualize connections between rankings across years
- Include color-coding for different categories/regions

## Design Elements to Include
- Left column: 2023 rankings
- Right column: 2024 rankings
- Flow connections showing movement between years when both rankings are in the top 10
- If an item was in the top 10 in 2023 but its ranking went beyond top 10 in 2024, show a small circle with its 2024 ranking
- If an item wasn't in the top 10 in 2023 but is in 2024, mark it as "new entry" and if possible show its previous rank beyond top 10
- Title and subtitle
- Legend for categories placed below the graph
- Source citation

## Technical Implementation
- Use Python with matplotlib, pandas, and potentially networkx for the flow visualization
- Create a command-line interface to generate the chart
- Allow for data input via JSON files (remove redundant create_sample_data function)
- Support customization of colors, titles, and other visual elements

## Dummy Data Structure
Countries of origin for movies seen, grouped by regions:
- North America (USA, Canada)
- Europe (UK, France, Italy, Spain, Germany)
- Asia (Japan, South Korea, China, India)
- Oceania (Australia, New Zealand)
- Latin America (Brazil, Mexico, Colombia)