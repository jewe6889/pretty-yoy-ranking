#!/usr/bin/env python3
"""
Generate a year-over-year ranking visualization for movie countries of origin.
"""

import argparse
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import pandas as pd
import json
from matplotlib.path import Path
from matplotlib.colors import to_rgba

# Define color scheme for regions
REGION_COLORS = {
    'North America': '#FF9F40',  # Orange
    'Europe': '#36A2EB',         # Blue
    'Asia': '#4BC0C0',           # Teal
    'South America': '#9966FF',  # Purple
    'Oceania': '#FF6384',        # Pink
    'Africa': '#FFCD56'          # Yellow
}

def get_rank_in_data(country, data):
    """Find the rank of a country in the data."""
    for item in data:
        if item['country'] == country:
            return item['rank']
    return None

def draw_flow_curve(ax, x1, y1, x2, y2, color, alpha=0.7, width=2.0):
    """Draw a Bezier curve between two points."""
    control_point_x = (x1 + x2) / 2
    verts = [
        (x1, y1),
        (control_point_x, y1),
        (control_point_x, y2),
        (x2, y2)
    ]
    codes = [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]
    path = Path(verts, codes)
    patch = patches.PathPatch(path, facecolor='none', edgecolor=color, alpha=alpha, lw=width)
    ax.add_patch(patch)

def create_visualization(data, output_file, title="Top 10 Movie Countries of Origin", subtitle=None):
    """Create the year-over-year ranking visualization."""
    # Create figure and axes
    fig, ax = plt.figure(figsize=(12, 10), dpi=300), plt.gca()
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    
    # Add title and subtitle
    plt.figtext(0.02, 0.97, title, fontsize=18, fontweight='bold')
    if subtitle:
        plt.figtext(0.02, 0.94, subtitle, fontsize=14)
    else:
        plt.figtext(0.02, 0.94, 
                    f"The top 10 countries of origin for movies watched in 2023 vs 2024",
                    fontsize=14)
    
    # Define positions
    left_col_x = 25
    right_col_x = 75
    spacing = 8.5  # Space between rankings
    top_y = 85     # Starting y position
    circle_radius = 2.5
    small_circle_radius = 1.2
    
    # Draw vertical line to separate the columns
    ax.axvline(x=50, ymin=0.2, ymax=0.9, color='lightgray', linestyle='-', alpha=0.8)
    
    # Add year labels
    plt.text(left_col_x, top_y + spacing, '2023', fontsize=16, fontweight='bold', ha='center')
    plt.text(right_col_x, top_y + spacing, '2024', fontsize=16, fontweight='bold', ha='center')
    
    # Get all data for the years
    data_2023_all = data.get('2023', [])
    data_2024_all = data.get('2024', [])
    
    # Filter to only show top 10
    data_2023 = [item for item in data_2023_all if item['rank'] <= 10]
    data_2024 = [item for item in data_2024_all if item['rank'] <= 10]
    
    # Create lookups for positions and countries in top 10
    positions_2023 = {}
    positions_2024 = {}
    countries_2023_top10 = set(item['country'] for item in data_2023)
    countries_2024_top10 = set(item['country'] for item in data_2024)
    
    # Create a lookup for full data
    country_region_2023 = {item['country']: item['region'] for item in data_2023_all}
    country_region_2024 = {item['country']: item['region'] for item in data_2024_all}
    
    # Draw 2023 rankings
    for i, item in enumerate(data_2023):
        y_pos = top_y - i * spacing
        positions_2023[item['country']] = (left_col_x, y_pos)
        
        # Draw circle
        circle = plt.Circle((left_col_x, y_pos), circle_radius, 
                           color=REGION_COLORS[item['region']], alpha=0.9)
        ax.add_artist(circle)
        
        # Add rank number
        plt.text(left_col_x, y_pos, str(item['rank']), fontsize=12, 
                 fontweight='bold', ha='center', va='center', color='white')
        
        # Add country name and percentage
        plt.text(left_col_x + 5, y_pos, 
                 f"{item['country']} ({item['percentage']}%)", 
                 fontsize=11, ha='left', va='center')
    
    # Draw 2024 rankings
    for i, item in enumerate(data_2024):
        y_pos = top_y - i * spacing
        positions_2024[item['country']] = (right_col_x, y_pos)
        
        # Draw circle
        circle = plt.Circle((right_col_x, y_pos), circle_radius, 
                           color=REGION_COLORS[item['region']], alpha=0.9)
        ax.add_artist(circle)
        
        # Add rank number
        plt.text(right_col_x, y_pos, str(item['rank']), fontsize=12, 
                 fontweight='bold', ha='center', va='center', color='white')
        
        # Add country name and percentage
        plt.text(right_col_x + 5, y_pos, 
                 f"{item['country']} ({item['percentage']}%)", 
                 fontsize=11, ha='left', va='center')
        
        # Check if it's a new entry (wasn't in top 10 last year)
        if item['country'] not in countries_2023_top10:
            # Check if we have a previous rank beyond top 10
            prev_rank = get_rank_in_data(item['country'], data_2023_all)
            if prev_rank:
                prev_indicator_x = right_col_x - 12
                # Use the same color as the parent circle
                indicator_color = REGION_COLORS[item['region']]
                indicator = plt.Circle((prev_indicator_x, y_pos), small_circle_radius, 
                                      color=indicator_color, alpha=0.9)
                ax.add_artist(indicator)
                plt.text(prev_indicator_x, y_pos, str(prev_rank), fontsize=8, 
                        ha='center', va='center', color='white')
                plt.text(right_col_x - 20, y_pos, "(new entry)", 
                        fontsize=8, ha='right', va='center', style='italic')
            else:
                plt.text(right_col_x - 12, y_pos, "(new entry)", 
                        fontsize=8, ha='right', va='center', style='italic')
    
    # Check for 2023 entries that are no longer in the top 10 in 2024
    for item in data_2023:
        if item['country'] not in countries_2024_top10:
            # Find an appropriate position on the right side
            # Use a position at the bottom, below the last entry in 2024 rankings
            y_pos = top_y - (len(data_2024) + 1) * spacing
            
            # Get 2024 rank if available
            new_rank = get_rank_in_data(item['country'], data_2024_all)
            
            # Draw a small indicator circle with the same color as the original
            indicator_x = right_col_x - 12
            indicator_color = REGION_COLORS[item['region']]
            indicator = plt.Circle((indicator_x, y_pos), small_circle_radius, 
                                  color=indicator_color, alpha=0.7)
            ax.add_artist(indicator)
            
            # Add the previous rank
            plt.text(indicator_x, y_pos, str(item['rank']), fontsize=8, 
                    ha='center', va='center', color='white')
            
            # Add country name and new rank if available
            if new_rank:
                plt.text(right_col_x - 8, y_pos, 
                        f"{item['country']} (now #{new_rank})", 
                        fontsize=9, ha='left', va='center', style='italic')
            else:
                plt.text(right_col_x - 8, y_pos, 
                        f"{item['country']} (out of top 20)", 
                        fontsize=9, ha='left', va='center', style='italic')
            
            # Only show one entry per row
            break
    
    # Draw connecting curves between entries in both years
    for country, (x2, y2) in positions_2024.items():
        if country in positions_2023:
            x1, y1 = positions_2023[country]
            # Get the color based on the region from the 2024 data
            color = REGION_COLORS[country_region_2024[country]]
            
            # Calculate width based on percentage
            for item in data_2024:
                if item['country'] == country:
                    width = item['percentage'] / 10  # Scale width by percentage
                    width = max(0.5, min(4.0, width))  # Clamp between 0.5 and 4.0
                    draw_flow_curve(ax, x1, y1, x2, y2, color, alpha=0.5, width=width)
                    break
    
    # Add region legend at the very bottom of the chart
    legend_y = 5  # Move further down
    legend_spacing_x = 16
    legend_start_x = 10
    
    for i, (region, color) in enumerate(REGION_COLORS.items()):
        # Create a 2-row legend if there are many categories
        if i >= 3:  # Switch to second row after 3 items
            row = 1
            col = i - 3
        else:
            row = 0
            col = i
        
        legend_x = legend_start_x + col * legend_spacing_x
        legend_row_y = legend_y - row * 4  # Space between rows
        
        circle = plt.Circle((legend_x, legend_row_y), 2, color=color)
        ax.add_artist(circle)
        plt.text(legend_x + 3, legend_row_y, region, fontsize=9, ha='left', va='center')
    
    # Add source citation
    plt.figtext(0.02, 0.01, "Source: Dummy data for illustration purposes", 
                fontsize=9, style='italic')
    
    # Save the figure
    plt.savefig(output_file, bbox_inches='tight', dpi=300)
    print(f"Visualization saved to {output_file}")

def load_data_from_json(json_file):
    """Load data from a JSON file."""
    with open(json_file, 'r') as f:
        return json.load(f)

def main():
    parser = argparse.ArgumentParser(description='Generate year-over-year ranking visualization.')
    parser.add_argument('-o', '--output', default='movie_countries_ranking.png',
                        help='Output file name (PNG format)')
    parser.add_argument('-t', '--title', default='Top 10 Movie Countries of Origin',
                        help='Chart title')
    parser.add_argument('-s', '--subtitle', 
                        help='Chart subtitle (defaults to a generated subtitle)')
    parser.add_argument('-d', '--data', default='sample_data.json',
                        help='Path to JSON file with ranking data')
    
    args = parser.parse_args()
    
    # Get data from file
    try:
        data = load_data_from_json(args.data)
    except Exception as e:
        print(f"Error loading data from {args.data}: {e}")
        print("Please provide a valid JSON data file.")
        return
    
    # Create visualization
    create_visualization(data, args.output, args.title, args.subtitle)

if __name__ == "__main__":
    main()