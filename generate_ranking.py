#!/usr/bin/env python3
"""
Generate a year-over-year ranking visualization for any type of ranked data.
Version 2.0 with integrated flow lines for dropped items.
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
import hashlib
from matplotlib.colors import hsv_to_rgb

# Set up high-quality visualization defaults
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
plt.rcParams['svg.fonttype'] = 'none'
plt.rcParams['axes.linewidth'] = 0.8
plt.rcParams['xtick.major.width'] = 0.8
plt.rcParams['ytick.major.width'] = 0.8
plt.rcParams['axes.titlepad'] = 12
plt.rcParams['figure.dpi'] = 300

# Fallback colors for backward compatibility - using generic group names
FALLBACK_COLORS = {
    'Group A': '#FF7F0E',  # Orange
    'Group B': '#1F77B4',  # Blue
    'Group C': '#2CA02C',  # Green
    'Group D': '#9467BD',  # Purple
    'Group E': '#D62728',  # Red
    'Group F': '#8C564B',  # Brown
    'Group G': '#E377C2',  # Pink
    'Group H': '#7F7F7F',  # Gray
    'Group I': '#BCBD22',  # Yellow-green
    'Group J': '#17BECF',  # Cyan
    'Unknown': '#8C8C8C'   # Grey for unknown categories
}

def generate_category_colors(categories):
    """
    Dynamically generate colors for categories.
    Uses a deterministic algorithm that will always produce the same color for the same category name.
    """
    color_dict = {}
    
    # Add special handling for common categories to maintain consistency with previous versions
    for category, color in FALLBACK_COLORS.items():
        color_dict[category] = color
    
    # High-contrast color palette (ensures good readability and distinction)
    base_colors = [
        '#1F77B4',  # Blue
        '#FF7F0E',  # Orange
        '#2CA02C',  # Green
        '#D62728',  # Red
        '#9467BD',  # Purple
        '#8C564B',  # Brown
        '#E377C2',  # Pink
        '#7F7F7F',  # Gray
        '#BCBD22',  # Yellow-green
        '#17BECF',  # Cyan
        '#AF7AA1',  # Mauve
        '#FE5F55',  # Salmon
        '#4B3B40',  # Dark gray
        '#9CAFB7',  # Light blue-gray
        '#566E3D',  # Olive green
        '#A5D8DD',  # Light blue
        '#E36588',  # Raspberry
        '#7FB069',  # Sage green
        '#D8973C',  # Amber
        '#965251',  # Burgundy
    ]
    
    # Generate a unique but consistent color for each category not in fallback
    for i, category in enumerate(categories):
        if category not in color_dict:
            if i < len(base_colors):
                color_dict[category] = base_colors[i]
            else:
                # For any additional categories, generate deterministic colors using the hash
                # This ensures the same category always gets the same color
                hash_obj = hashlib.md5(category.encode())
                hash_hex = hash_obj.hexdigest()
                
                # Convert the hash to HSV values with good saturation and value
                # for visibility, then convert to RGB
                h = int(hash_hex[:2], 16) / 255.0  # Hue from first byte
                s = 0.7 + (int(hash_hex[2:4], 16) / 255.0) * 0.3  # Saturation 0.7-1.0
                v = 0.6 + (int(hash_hex[4:6], 16) / 255.0) * 0.3  # Value 0.6-0.9
                
                rgb = hsv_to_rgb((h, s, v))
                hex_color = '#{:02x}{:02x}{:02x}'.format(
                    int(rgb[0]*255),
                    int(rgb[1]*255),
                    int(rgb[2]*255)
                )
                color_dict[category] = hex_color
    
    return color_dict

def get_rank_in_data(item_name, data):
    """Find the rank of an item in the data."""
    for item in data:
        if item['item'] == item_name:
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

def create_visualization(data, output_file, title="Top 10 Ranked Items", subtitle=None, 
                         max_entries_override=None):
    """Create the year-over-year ranking visualization with enhanced styling."""
    # Create figure and axes with improved proportions
    fig = plt.figure(figsize=(12, 10), dpi=300) # Adjusted figsize slightly
    
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
    plt.figtext(0.05, 0.95, title, fontsize=20, fontweight='bold',
                color='#232323', ha='left',
                bbox=dict(facecolor='none', edgecolor='none', pad=0))
    
    # Get years dynamically from data instead of hardcoding
    years = sorted(data.keys())
    if len(years) < 2:
        print("Warning: Data must contain at least two years. Using placeholder years.")
        years = ["Previous Year", "Current Year"]
    
    # Use the last two years if more than two are provided
    prev_year = years[-2]
    curr_year = years[-1]
    
    if subtitle:
        plt.figtext(0.05, 0.91, subtitle, fontsize=14,
                    color='#5A5A5A', ha='left')
    else:
        # Use dynamic years in subtitle
        plt.figtext(0.05, 0.91, 
                    f"Comparison of rankings between {prev_year} and {curr_year}",
                    fontsize=14, color='#5A5A5A', ha='left')
    
    # Define positions with optimized spacing - adjusted X positions
    left_col_x = 25  # Moved left as edge area is removed
    right_col_x = 75
    spacing = 6.0       # Adjusted spacing slightly
    top_y = 80          # Adjusted starting y position
    circle_radius = 2.5
    small_circle_radius = 1.2
    
    # Draw vertical line to separate the columns with improved styling
    ax.axvline(x=50, ymin=0.15, ymax=0.85, color='#DDDDDD', linestyle='-', alpha=0.9, lw=1.2, zorder=0)
    
    # Add year labels with enhanced typography - use dynamic years
    plt.text(left_col_x, top_y + spacing, prev_year, fontsize=16, fontweight='bold',
             ha='center', va='center', color='#232323')
    plt.text(right_col_x, top_y + spacing, curr_year, fontsize=16, fontweight='bold',
             ha='center', va='center', color='#232323')
    
    # Get all data for the years - use dynamic years
    data_prev_all = data.get(prev_year, [])
    data_curr_all = data.get(curr_year, [])
    
    # Determine how many entries to show (up to 10 or max available or override)
    if max_entries_override is not None:
        max_entries = min(max_entries_override, max(len(data_prev_all), len(data_curr_all)))
    else:
        max_entries = min(10, max(len(data_prev_all), len(data_curr_all)))
    
    # Filter to show the determined number of entries - use dynamic years
    data_prev = [item for item in data_prev_all if item['rank'] <= max_entries]
    data_curr = [item for item in data_curr_all if item['rank'] <= max_entries]
    
    # Create lookups for positions and items
    positions_prev = {}
    positions_curr = {}
    items_prev_top = set(item['item'] for item in data_prev)
    items_curr_top = set(item['item'] for item in data_curr)
    
    # Create a lookup for full data
    item_category_prev = {item['item']: item.get('category', 'Unknown') for item in data_prev_all}
    item_category_curr = {item['item']: item.get('category', 'Unknown') for item in data_curr_all}
    
    # Get all unique categories from the data
    all_categories = set(item_category_prev.values()) | set(item_category_curr.values())
    
    # Generate colors for all categories
    global CATEGORY_COLORS
    CATEGORY_COLORS = generate_category_colors(all_categories)
    
    # Add subtle alternating row backgrounds for better readability
    for i in range(max_entries):
        if i % 2 == 0:  # Alternating rows
            y_top = top_y - (i * spacing) + (spacing / 2)
            y_bottom = top_y - ((i+1) * spacing) + (spacing / 2)
            height = y_top - y_bottom
            
            # Create a subtle background for even rows
            row_bg = plt.Rectangle((5, y_bottom), 90, height, fc='#F5F7F9',
                                  ec='none', alpha=0.6, zorder=0)
            ax.add_patch(row_bg)
    
    # Draw horizontal separator lines with improved styling (only where needed)
    for i in range(1, max_entries):
        y_pos = top_y - (i * spacing) + (spacing / 2)
        plt.axhline(y=y_pos, xmin=0.05, xmax=0.95, color='#DDDDDD',
                   linestyle='dotted', alpha=0.8, linewidth=0.8, zorder=1)
    
    # Draw previous year rankings with enhanced styling
    for i, item in enumerate(data_prev):
        y_pos = top_y - i * spacing
        positions_prev[item['item']] = (left_col_x, y_pos)
        
        # Add subtle shadow for depth
        shadow = plt.Circle((left_col_x + 0.15, y_pos - 0.15), circle_radius,
                          color='#00000015', zorder=2)
        ax.add_artist(shadow)
        
        # Draw circle with enhanced styling - use get for category
        category = item.get('category', 'Unknown')
        circle = plt.Circle((left_col_x, y_pos), circle_radius, 
                           color=CATEGORY_COLORS[category], alpha=0.9,
                           ec='white', lw=0.7, zorder=3)  # White edge
        ax.add_artist(circle)
        
        # Add rank number with perfect centering and enhanced style
        plt.text(left_col_x, y_pos, str(item['rank']), 
                 fontsize=11, fontweight='bold', 
                 ha='center', va='center', 
                 color='white', zorder=4)
        
        # Add item name with improved typography and alignment
        plt.text(left_col_x + 5, y_pos, 
                 f"{item['item']}", 
                 fontsize=11, ha='left', va='center', 
                 color='#232323', zorder=4)
        
        # Add percentage/value with improved styling and positioning
        value_text = ""
        if 'percentage' in item:
            value_text = f"{item['percentage']}%"
        elif 'value' in item:
            # Format value nicely if it's numeric
            try:
                value_text = f"{float(item['value']):.2f}"
            except (ValueError, TypeError):
                value_text = str(item['value']) # Fallback to string if not float

        if value_text:
            plt.text(left_col_x + 5, y_pos - 1.5,
                    value_text,
                    fontsize=9, ha='left', va='center', 
                    color='#5A5A5A', fontstyle='italic', zorder=4)
    
    # Draw current year rankings with enhanced styling
    for i, item in enumerate(data_curr):
        y_pos = top_y - i * spacing
        positions_curr[item['item']] = (right_col_x, y_pos)
        
        # Add subtle shadow for depth
        shadow = plt.Circle((right_col_x + 0.15, y_pos - 0.15), circle_radius,
                          color='#00000015', zorder=2)
        ax.add_artist(shadow)
        
        # Draw circle with enhanced styling - use get for category
        category = item.get('category', 'Unknown')
        circle = plt.Circle((right_col_x, y_pos), circle_radius, 
                           color=CATEGORY_COLORS[category], alpha=0.9,
                           ec='white', lw=0.7, zorder=3)  # White edge
        ax.add_artist(circle)
        
        # Add rank number with perfect centering and enhanced style
        plt.text(right_col_x, y_pos, str(item['rank']), 
                 fontsize=11, fontweight='bold', 
                 ha='center', va='center', 
                 color='white', zorder=4)
        
        # Add item name with improved typography and alignment
        plt.text(right_col_x + 5, y_pos, 
                 f"{item['item']}", 
                 fontsize=11, ha='left', va='center', 
                 color='#232323', zorder=4)
        
        # Add percentage/value with improved styling and positioning
        value_text = ""
        if 'percentage' in item:
            value_text = f"{item['percentage']}%"
        elif 'value' in item:
            # Format value nicely if it's numeric
            try:
                value_text = f"{float(item['value']):.2f}"
            except (ValueError, TypeError):
                value_text = str(item['value']) # Fallback to string if not float

        if value_text:
            plt.text(right_col_x + 5, y_pos - 1.5,
                    value_text,
                    fontsize=9, ha='left', va='center', 
                    color='#5A5A5A', fontstyle='italic', zorder=4)
        
        # Check if it's a new entry with enhanced styling
        if item['item'] not in items_prev_top:
            # Check if we have a previous rank beyond top shown
            prev_rank = get_rank_in_data(item['item'], data_prev_all)
            if prev_rank:
                prev_indicator_x = right_col_x - 12
                
                # Add subtle shadow for depth
                shadow = plt.Circle((prev_indicator_x + 0.15, y_pos - 0.15), small_circle_radius,
                                  color='#00000015', zorder=2)
                ax.add_artist(shadow)
                
                # Use the same color as the parent circle with enhanced styling - use get for category
                indicator_category = item.get('category', 'Unknown')
                indicator_color = CATEGORY_COLORS[indicator_category]
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
    
    # Draw connecting curves between entries in both years
    for item, (x2, y2) in positions_curr.items():
        if item in positions_prev:
            x1, y1 = positions_prev[item]
            
            # Get colors for start and end points - use get for category
            start_category = item_category_prev.get(item, 'Unknown')
            end_category = item_category_curr.get(item, 'Unknown')
            start_color = CATEGORY_COLORS[start_category]
            end_color = CATEGORY_COLORS[end_category]
            
            # Calculate rank change - use dynamic year logic
            start_rank = get_rank_in_data(item, data_prev_all) # Use all data for correct rank change calc
            end_rank = get_rank_in_data(item, data_curr_all)
            rank_change = None
            if start_rank is not None and end_rank is not None:
                 rank_change = start_rank - end_rank # Positive means moved up, negative means moved down
            
            # Calculate line width based on percentage/value or default
            width = 1.5 # Default width
            item_curr_data = next((data_item for data_item in data_curr_all if data_item['item'] == item), None)
            if item_curr_data:
                if 'percentage' in item_curr_data:
                    perc = item_curr_data['percentage']
                    width = max(0.6, min(2.8, (perc / 25) + 0.6))
                elif 'value' in item_curr_data:
                    # Use value for width if percentage is missing, needs scaling
                    try:
                        val = float(item_curr_data['value'])
                        # Example scaling: Adjust based on expected value range
                        # Assuming values are roughly comparable to percentages / 10
                        width = max(0.6, min(2.8, (val * 2.5) + 0.6)) 
                    except (ValueError, TypeError):
                        width = 1.5 # Fallback width if value isn't numeric
            
            # Draw improved flow line with enhanced styling
            draw_flow_curve(ax, x1, y1, x2, y2, start_color, end_color, 
                           alpha=0.65, width=width, rank_change=rank_change)
    
    # Create a legend container with subtle styling - adjusted position/size
    legend_container = plt.Rectangle((5, 1), 90, 12, fc='#FAFAFA',
                                   ec='#E5E5E5', linewidth=0.8, 
                                   alpha=0.9, zorder=1)
    ax.add_patch(legend_container)
    
    # Add category legend with fully dynamic layout
    legend_y = 8  # Starting y position
    legend_x_start = 10  # Starting x position
    legend_x_spacing = 30  # Horizontal spacing between categories
    legend_y_spacing = 2.7  # Vertical spacing between categories
    
    # Get all active categories (ones that actually appear in the data)
    active_categories = sorted(list(
        set(item_category_prev.values()) | set(item_category_curr.values())
    ))
    
    # Calculate how many categories to place in each column (max 4 per column)
    items_per_column = min(4, max(1, len(active_categories) // 3 + 1))
    
    # Draw category circles with their labels
    for i, category in enumerate(active_categories):
        # Calculate position in the grid
        column = i // items_per_column
        row = i % items_per_column
        
        # Set x and y coordinates
        category_x = legend_x_start + (column * legend_x_spacing)
        category_y = legend_y - (row * legend_y_spacing)
        
        # Add subtle shadow
        shadow = plt.Circle((category_x + 0.1, category_y - 0.1), 1.5, 
                           color='#00000015', zorder=2)
        ax.add_artist(shadow)
        
        # Draw circle with color from our generated color dictionary
        category_color = CATEGORY_COLORS.get(category, CATEGORY_COLORS['Unknown'])
        circle = plt.Circle((category_x, category_y), 1.5, 
                           color=category_color, alpha=0.9,
                           ec='white', lw=0.5, zorder=3)
        ax.add_artist(circle)
        
        # Add category name with improved typography
        plt.text(category_x + 3, category_y, category, 
                fontsize=9, ha='left', va='center', 
                color='#333333', zorder=4)
    
    # Save the figure with enhanced quality settings
    plt.savefig(output_file, bbox_inches='tight', dpi=300, 
               facecolor='white', edgecolor='none')
    print(f"Version 2.0 visualization saved to {output_file}")

def load_data_from_json(json_file):
    """Load data from a JSON file."""
    with open(json_file, 'r') as f:
        return json.load(f)

def main():
    parser = argparse.ArgumentParser(description='Generate year-over-year ranking visualization.')
    parser.add_argument('-o', '--output', default='ranking_v2.png',
                        help='Output file name (PNG format)')
    parser.add_argument('-t', '--title', default='Top 10 Ranked Items',
                        help='Chart title')
    parser.add_argument('-s', '--subtitle', 
                        help='Chart subtitle (defaults to a generated subtitle)')
    parser.add_argument('-d', '--data', default='sample_data.json',
                        help='Path to JSON file with ranking data')
    parser.add_argument('--max-entries', type=int,
                        help='Maximum number of entries to show (default is 10)')
    
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
    
    # Create visualization with all customization options
    create_visualization(
        data, 
        args.output, 
        args.title, 
        args.subtitle,
        args.max_entries
    )

if __name__ == "__main__":
    main()