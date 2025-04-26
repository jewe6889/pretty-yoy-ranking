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
from matplotlib.colors import to_rgba, LinearSegmentedColormap
import matplotlib.patheffects as PathEffects
from matplotlib import rcParams

# Set up high-quality visualization defaults
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
plt.rcParams['svg.fonttype'] = 'none'
plt.rcParams['axes.linewidth'] = 0.8
plt.rcParams['xtick.major.width'] = 0.8
plt.rcParams['ytick.major.width'] = 0.8
plt.rcParams['axes.titlepad'] = 12
plt.rcParams['figure.dpi'] = 300

# Enhanced color scheme for regions with improved contrast and print compatibility
REGION_COLORS = {
    'North America': '#FF7F0E',  # Darker orange for better contrast
    'Europe': '#1F77B4',         # Darker blue
    'Asia': '#2CA02C',           # Richer green
    'South America': '#9467BD',  # Richer purple
    'Oceania': '#D62728',        # Darker red
    'Africa': '#E6B417'          # Richer yellow
}

def get_rank_in_data(country, data):
    """Find the rank of a country in the data."""
    for item in data:
        if item['country'] == country:
            return item['rank']
    return None

def create_color_gradient(start_color, end_color, n=100):
    """Create a gradient color map between two colors."""
    cmap = LinearSegmentedColormap.from_list("custom_gradient", [start_color, end_color], N=n)
    return cmap

def draw_flow_curve(ax, x1, y1, x2, y2, start_color, end_color, alpha=0.7, width=2.0, rank_change=None):
    """Draw a Bezier curve between two points with gradient color and rank change indicator."""
    # Create gradient for the line with smoother transitions
    cmap = create_color_gradient(start_color, end_color)
    
    # Improved control points for more elegant curves
    # Adjust these parameters based on the distance and vertical change
    x_dist = abs(x2 - x1)
    y_dist = abs(y2 - y1)
    
    # Dynamic control points based on distance
    control_shift = min(x_dist * 0.4, 18)  # Less aggressive control points
    
    # Create points with improved logic for smoother lines
    control_point1_x = x1 + control_shift
    control_point2_x = x2 - control_shift
    
    # Create path for the curve with improved control points
    curve_points = np.array([
        [x1, y1],
        [control_point1_x, y1],
        [control_point2_x, y2],
        [x2, y2]
    ])
    
    # Generate smoother curve with more points
    x = np.linspace(0, 1, 150)  # More points for smoother gradient
    curve = np.array([
        (1-x)**3 * curve_points[0] +
        3*(1-x)**2 * x * curve_points[1] +
        3*(1-x) * x**2 * curve_points[2] +
        x**3 * curve_points[3]
        for x in x
    ])
    
    # Draw the curve segments with gradient color with z-order control
    segments = []
    for i in range(len(curve) - 1):
        t = i / (len(curve) - 1)
        color = cmap(t)
        segment = plt.Line2D(
            [curve[i][0], curve[i+1][0]],
            [curve[i][1], curve[i+1][1]],
            color=color,
            alpha=alpha,
            linewidth=width,
            zorder=5  # Place below rank indicators but above background
        )
        segments.append(segment)
        ax.add_artist(segment)
    
    # Add rank change indicator if specified with improved styling
    if rank_change is not None:
        # Position the indicator in the middle of the curve with slight offset
        mid_point_idx = len(curve) // 2
        mid_x, mid_y = curve[mid_point_idx]
        
        # Enhanced indicator design with drop shadow effect
        indicator_size = 2.0  # Slightly larger for better visibility
        indicator_color = '#FFFFFF'  # White background
        border_color = '#555555'     # Grey border
        
        # Add subtle shadow for depth (slightly offset darker circle)
        shadow = plt.Circle(
            (mid_x + 0.3, mid_y - 0.3),
            indicator_size,
            color='#00000022',
            zorder=9
        )
        ax.add_artist(shadow)
        
        # Main indicator circle with border
        indicator = plt.Circle(
            (mid_x, mid_y),
            indicator_size,
            color=indicator_color,
            ec=border_color,
            lw=0.8,
            zorder=10
        )
        ax.add_artist(indicator)
        
        # Format rank change text with improved styling
        if rank_change > 0:
            rank_text = f"+{rank_change}"
            text_color = '#18840B'  # Darker green for better contrast
        elif rank_change < 0:
            rank_text = f"{rank_change}"
            text_color = '#B91D1D'  # Darker red
        else:
            rank_text = "0"
            text_color = '#555555'  # Grey
        
        # Add the rank change text with enhanced styling
        text = plt.text(
            mid_x, mid_y,
            rank_text,
            color=text_color,
            ha='center',
            va='center',
            fontsize=8.5,  # Slightly larger
            fontweight='bold',
            zorder=11
        )
        
        # Add enhanced shadow effect to make the text stand out
        text.set_path_effects([
            PathEffects.withStroke(linewidth=2.5, foreground='white')
        ])

def create_visualization(data, output_file, title="Top 10 Movie Countries of Origin", subtitle=None):
    """Create the year-over-year ranking visualization with enhanced styling."""
    # Create figure and axes with improved proportions
    fig = plt.figure(figsize=(14, 11), dpi=300)
    
    # Create background with subtle gradient for more professional look
    ax = plt.gca()
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    
    # Add subtle background with gradient
    background = plt.Rectangle((0, 0), 100, 100, fc='#F8F9FA', ec='none', zorder=-10)
    ax.add_patch(background)
    
    # Add a subtle container for the main content
    content_bg = plt.Rectangle((5, 15), 90, 75, fc='#ffffff', ec='#E5E5E5', 
                             alpha=0.7, zorder=-5, linewidth=0.5)
    ax.add_patch(content_bg)
    
    # Add title and subtitle with enhanced typography
    plt.figtext(0.05, 0.95, title, fontsize=22, fontweight='bold', 
                color='#232323', ha='left',
                bbox=dict(facecolor='none', edgecolor='none', pad=0))
    
    if subtitle:
        plt.figtext(0.05, 0.91, subtitle, fontsize=15, 
                    color='#5A5A5A', ha='left')
    else:
        plt.figtext(0.05, 0.91, 
                    f"The top 10 countries of origin for movies watched in 2023 vs 2024",
                    fontsize=15, color='#5A5A5A', ha='left')
    
    # Define positions with optimized spacing
    left_col_x = 25
    right_col_x = 75
    spacing = 6.8       # Refined spacing for more compact layout
    top_y = 82          # Adjusted starting y position
    circle_radius = 2.5
    small_circle_radius = 1.2
    
    # Draw vertical line to separate the columns with improved styling
    ax.axvline(x=50, ymin=0.2, ymax=0.85, color='#DDDDDD', linestyle='-', alpha=0.9, lw=1.2, zorder=0)
    
    # Add year labels with enhanced typography
    plt.text(left_col_x, top_y + spacing, '2023', fontsize=18, fontweight='bold', 
             ha='center', va='center', color='#232323')
    plt.text(right_col_x, top_y + spacing, '2024', fontsize=18, fontweight='bold', 
             ha='center', va='center', color='#232323')
    
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
    
    # Add subtle alternating row backgrounds for better readability
    for i in range(10):
        if i % 2 == 0:  # Alternating rows
            y_top = top_y - (i * spacing) + (spacing / 2)
            y_bottom = top_y - ((i+1) * spacing) + (spacing / 2)
            height = y_top - y_bottom
            
            # Create a subtle background for even rows
            row_bg = plt.Rectangle((8, y_bottom), 84, height, fc='#F5F7F9', 
                                  ec='none', alpha=0.6, zorder=0)
            ax.add_patch(row_bg)
    
    # Draw horizontal separator lines with improved styling (only where needed)
    for i in range(1, 10):
        y_pos = top_y - (i * spacing) + (spacing / 2)
        plt.axhline(y=y_pos, xmin=0.08, xmax=0.92, color='#DDDDDD', 
                   linestyle='dotted', alpha=0.8, linewidth=0.8, zorder=1)
    
    # Draw 2023 rankings with enhanced styling
    for i, item in enumerate(data_2023):
        y_pos = top_y - i * spacing
        positions_2023[item['country']] = (left_col_x, y_pos)
        
        # Add subtle shadow for depth
        shadow = plt.Circle((left_col_x + 0.15, y_pos - 0.15), circle_radius,
                          color='#00000015', zorder=2)
        ax.add_artist(shadow)
        
        # Draw circle with enhanced styling
        circle = plt.Circle((left_col_x, y_pos), circle_radius, 
                           color=REGION_COLORS[item['region']], alpha=0.9,
                           ec='white', lw=0.7, zorder=3)  # White edge
        ax.add_artist(circle)
        
        # Add rank number with perfect centering and enhanced style
        plt.text(left_col_x, y_pos, str(item['rank']), 
                 fontsize=11, fontweight='bold', 
                 ha='center', va='center', 
                 color='white', zorder=4)
        
        # Add country name with improved typography and alignment
        plt.text(left_col_x + 5, y_pos, 
                 f"{item['country']}", 
                 fontsize=11, ha='left', va='center', 
                 color='#232323', zorder=4)
        
        # Add percentage with improved styling and positioning
        plt.text(left_col_x + 5, y_pos - 1.5,
                f"{item['percentage']}%",
                fontsize=9, ha='left', va='center', 
                color='#5A5A5A', fontstyle='italic', zorder=4)
    
    # Draw 2024 rankings with enhanced styling
    for i, item in enumerate(data_2024):
        y_pos = top_y - i * spacing
        positions_2024[item['country']] = (right_col_x, y_pos)
        
        # Add subtle shadow for depth
        shadow = plt.Circle((right_col_x + 0.15, y_pos - 0.15), circle_radius,
                          color='#00000015', zorder=2)
        ax.add_artist(shadow)
        
        # Draw circle with enhanced styling
        circle = plt.Circle((right_col_x, y_pos), circle_radius, 
                           color=REGION_COLORS[item['region']], alpha=0.9,
                           ec='white', lw=0.7, zorder=3)  # White edge
        ax.add_artist(circle)
        
        # Add rank number with perfect centering and enhanced style
        plt.text(right_col_x, y_pos, str(item['rank']), 
                 fontsize=11, fontweight='bold', 
                 ha='center', va='center', 
                 color='white', zorder=4)
        
        # Add country name with improved typography and alignment
        plt.text(right_col_x + 5, y_pos, 
                 f"{item['country']}", 
                 fontsize=11, ha='left', va='center', 
                 color='#232323', zorder=4)
        
        # Add percentage with improved styling and positioning
        plt.text(right_col_x + 5, y_pos - 1.5,
                f"{item['percentage']}%",
                fontsize=9, ha='left', va='center', 
                color='#5A5A5A', fontstyle='italic', zorder=4)
        
        # Check if it's a new entry with enhanced styling
        if item['country'] not in countries_2023_top10:
            # Check if we have a previous rank beyond top 10
            prev_rank = get_rank_in_data(item['country'], data_2023_all)
            if prev_rank:
                prev_indicator_x = right_col_x - 12
                
                # Add subtle shadow for depth
                shadow = plt.Circle((prev_indicator_x + 0.15, y_pos - 0.15), small_circle_radius,
                                  color='#00000015', zorder=2)
                ax.add_artist(shadow)
                
                # Use the same color as the parent circle with enhanced styling
                indicator_color = REGION_COLORS[item['region']]
                indicator = plt.Circle((prev_indicator_x, y_pos), small_circle_radius, 
                                      color=indicator_color, alpha=0.9,
                                      ec='white', lw=0.5, zorder=3)
                ax.add_artist(indicator)
                
                # Add rank number with enhanced styling
                plt.text(prev_indicator_x, y_pos, str(prev_rank), 
                        fontsize=8, ha='center', va='center', 
                        color='white', zorder=4)
                
                # More elegant new entry label with enhanced styling
                plt.text(right_col_x - 19, y_pos, "NEW", 
                        fontsize=7.5, ha='right', va='center', 
                        style='italic', color='#444444', fontweight='bold',
                        bbox=dict(boxstyle="round,pad=0.4", fc="#f0f0f0", ec="#E0E0E0", 
                                alpha=0.9), zorder=4)
            else:
                # More elegant new entry label with enhanced styling
                plt.text(right_col_x - 12, y_pos, "NEW", 
                        fontsize=7.5, ha='right', va='center', 
                        style='italic', color='#444444', fontweight='bold',
                        bbox=dict(boxstyle="round,pad=0.4", fc="#f0f0f0", ec="#E0E0E0", 
                                alpha=0.9), zorder=4)
    
    # MOVED: Create a "dropped from top 10" section on the LEFT side
    dropped_entries_shown = 0
    dropped_entries = [item for item in data_2023 if item['country'] not in countries_2024_top10]
    
    if dropped_entries:
        # Create section container on left side
        dropped_container_y = 30
        dropped_container_height = 15
        dropped_container = plt.Rectangle((8, dropped_container_y - dropped_container_height), 
                                        34, dropped_container_height, 
                                        fc='#F5F7F9', ec='#E0E0E0', 
                                        linewidth=0.8, alpha=0.8, zorder=1)
        ax.add_patch(dropped_container)
        
        # Add a heading for this section
        plt.text(10, dropped_container_y - 2, 
                "Dropped from Top 10:", 
                fontsize=9, ha='left', va='top', 
                color='#555555', fontweight='bold', zorder=4)
        
        # Process dropped entries
        for i, item in enumerate(dropped_entries):
            # Position entries within the container
            y_pos = dropped_container_y - 5 - (i * 3.5)
            
            # Get 2024 rank if available
            new_rank = get_rank_in_data(item['country'], data_2024_all)
            
            # Add subtle shadow for depth
            shadow = plt.Circle((12.15, y_pos - 0.15), small_circle_radius,
                              color='#00000015', zorder=2)
            ax.add_artist(shadow)
            
            # Draw a small indicator circle with enhanced styling
            indicator_color = REGION_COLORS[item['region']]
            indicator = plt.Circle((12, y_pos), small_circle_radius, 
                                  color=indicator_color, alpha=0.9,
                                  ec='white', lw=0.5, zorder=3)
            ax.add_artist(indicator)
            
            # Add the previous rank with enhanced styling
            plt.text(12, y_pos, str(item['rank']), 
                    fontsize=8, ha='center', va='center', 
                    color='white', zorder=4)
            
            # Add country name and new rank with improved styling
            plt.text(15, y_pos, 
                    f"{item['country']}", 
                    fontsize=9, ha='left', va='center', 
                    color='#444444', zorder=4)
            
            # Add 2024 status
            if new_rank:
                plt.text(28, y_pos,
                        f"→ #{new_rank}", 
                        fontsize=8.5, ha='left', va='center', 
                        color='#666666', zorder=4)
            else:
                plt.text(28, y_pos,
                        "→ out", 
                        fontsize=8.5, ha='left', va='center', 
                        color='#666666', zorder=4)
            
            dropped_entries_shown += 1
            if dropped_entries_shown >= 3:
                break
    
    # Draw connecting curves between entries in both years
    for country, (x2, y2) in positions_2024.items():
        if country in positions_2023:
            x1, y1 = positions_2023[country]
            
            # Get colors for start and end points
            start_region = country_region_2023[country]
            end_region = country_region_2024[country]
            start_color = REGION_COLORS[start_region]
            end_color = REGION_COLORS[end_region]
            
            # Calculate rank change
            start_rank = get_rank_in_data(country, data_2023)
            end_rank = get_rank_in_data(country, data_2024)
            rank_change = start_rank - end_rank  # Positive means moved up, negative means moved down
            
            # Calculate line width based on percentage with refined scaling
            for item in data_2024:
                if item['country'] == country:
                    # More refined width calculation
                    perc = item['percentage']
                    width = (perc / 25) + 0.6  # Better scaling
                    width = max(0.6, min(2.8, width))  # Refined clamping
                    # Draw improved flow line with enhanced styling
                    draw_flow_curve(ax, x1, y1, x2, y2, start_color, end_color, 
                                   alpha=0.65, width=width, rank_change=rank_change)
                    break
    
    # Create a legend container with subtle styling
    legend_container = plt.Rectangle((7, 1), 86, 12, fc='#FAFAFA', 
                                   ec='#E5E5E5', linewidth=0.8, 
                                   alpha=0.9, zorder=1)
    ax.add_patch(legend_container)
    
    # Add region legend with enhanced grouping and styling
    legend_y = 8  # Adjusted positioning
    
    # Group regions by continent for better organization
    continent_groups = {
        'Americas': ['North America', 'South America'],
        'Europe & Africa': ['Europe', 'Africa'],
        'Asia-Pacific': ['Asia', 'Oceania']
    }
    
    # Draw group headers with improved styling
    group_x_positions = [12, 42, 72]
    
    for i, (group_name, regions) in enumerate(continent_groups.items()):
        group_x = group_x_positions[i]
        plt.text(group_x, legend_y + 2.5, group_name, 
                fontsize=9.5, fontweight='bold', ha='left', va='center',
                color='#454545', zorder=4)
        
        # Draw regions in each group with enhanced styling
        for j, region in enumerate(regions):
            region_x = group_x + 1
            region_y = legend_y - j * 2.7
            
            # Add subtle shadow
            shadow = plt.Circle((region_x + 0.1, region_y - 0.1), 1.5, 
                               color='#00000015', zorder=2)
            ax.add_artist(shadow)
            
            # Draw circle with improved styling
            circle = plt.Circle((region_x, region_y), 1.5, 
                               color=REGION_COLORS[region], alpha=0.9,
                               ec='white', lw=0.5, zorder=3)
            ax.add_artist(circle)
            
            # Add region name with improved typography
            plt.text(region_x + 3, region_y, region, 
                    fontsize=9, ha='left', va='center', 
                    color='#333333', zorder=4)
    
    # Add enhanced source citation
    plt.figtext(0.07, 0.02, "Source: Dummy data for illustration purposes", 
                fontsize=8, style='italic', color='#777777')
    
    # Add watermark/credit
    plt.figtext(0.93, 0.02, "Generated with pretty-yoy-ranking", 
               fontsize=7, style='italic', color='#AAAAAA', ha='right')
    
    # Save the figure with enhanced quality settings
    plt.savefig(output_file, bbox_inches='tight', dpi=300, 
               facecolor='white', edgecolor='none')
    print(f"Publication-ready visualization saved to {output_file}")

def load_data_from_json(json_file):
    """Load data from a JSON file."""
    with open(json_file, 'r') as f:
        return json.load(f)

def main():
    parser = argparse.ArgumentParser(description='Generate year-over-year ranking visualization.')
    parser.add_argument('-o', '--output', default='publication_ready_ranking.png',
                        help='Output file name (PNG format)')
    parser.add_argument('-t', '--title', default='Top 10 Movie Countries of Origin',
                        help='Chart title')
    parser.add_argument('-s', '--subtitle', 
                        help='Chart subtitle (defaults to a generated subtitle)')
    parser.add_argument('-d', '--data', default='sample_data.json',
                        help='Path to JSON file with ranking data')
    
    args = parser.parse_args()
    
    # Get data from file with improved error handling
    try:
        data = load_data_from_json(args.data)
    except FileNotFoundError:
        print(f"Error: Data file '{args.data}' not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: '{args.data}' is not a valid JSON file.")
        return
    except Exception as e:
        print(f"Error loading data from {args.data}: {e}")
        print("Please provide a valid JSON data file.")
        return
    
    # Create visualization
    create_visualization(data, args.output, args.title, args.subtitle)

if __name__ == "__main__":
    main()