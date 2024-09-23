import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import matplotlib.colors as mcolors

def plot_demand(results_df):
    # Calculate contributions from Rice Husk zones
    for zone in range(1, 6):
        results_df[f'rice_husk_zone_{zone}'] = results_df['rice_husk_boiler'] * results_df[f'rice_husk_zone_{zone}']
    
    # Combine the data into a new DataFrame for plotting
    plot_data = results_df[['natural_gas_boiler', 'wood_pellet_boiler'] + [f'rice_husk_zone_{zone}' for zone in range(1, 6)]]
    
    # Plotting
    fig, ax1 = plt.subplots(figsize=(7, 4))
    
    # Colors: 5 similar shades of green, plus colors for natural gas and wood pellets
    colors = ['#2E86C1', '#E67E22', '#1E8449', '#229954', '#27AE60', '#2ECC71', '#82E0AA']
    
    # Create a stacked bar plot
    plot_data.plot(kind='bar', stacked=True, ax=ax1, color=colors, edgecolor='black')
    
    # Set the x-axis to the final demand values
    ax1.set_xticks(range(len(results_df['demand'])))
    ax1.set_xticklabels([f'{x:.2f}' for x in results_df['demand']])
    
    # Set labels and title
    ax1.set_xlabel('Final Demand for Processed Rice (in Mt/year)')
    ax1.set_ylabel('Thermal Energy Production Mix [-]')
    ax1.set_title('Thermal Energy Source Distribution')
    ax1.set_ylim(0, 1)
    
    # Add a scatter plot that doesn't show up in the plot area but is included in the legend
    ax1.scatter([np.nan], [np.nan], color='red', edgecolor='black', label='GWP')
    
    # Adjust legend
    ax1.legend(['GWP', 'Natural Gas', 'Wood Pellets', 'R. Husk Zone 1', 'R. Husk Zone 2', 
                'R. Husk Zone 3', 'R. Husk Zone 4', 'R. Husk Zone 5'], 
               loc='upper center', bbox_to_anchor=(0.5, 1.28), ncol=4)
    
    # Create a second y-axis for the GWP impact
    ax2 = ax1.twinx()
    ax2.plot(range(len(results_df['demand'])), results_df['impact'], color='red', markeredgecolor='black', marker='o', linestyle='')
    ax2.set_ylabel('GWP (in Mt CO₂-eq)')
    
    # Show the plot
    plt.show()


def plot_pareto(pareto_front):
    # Convert pareto_front into two separate lists for plotting
    costs, gwps = zip(*pareto_front)
    
    # Create the Pareto front plot
    plt.figure(figsize=(5, 4))
    plt.plot(costs, gwps, marker='o', color='b', linestyle=':', linewidth=2, markersize=10, markeredgecolor='black')
    
    # Set labels
    plt.xlabel('Cost (in $/kg pr. rice)', fontsize=14)
    plt.ylabel('GWP (in kg CO₂-eq/kg pr. rice)', fontsize=14)
    
    # Add grid for better readability
    plt.grid(True)
    
    plt.show()

def plot_cases():      
    # Data
    scenarios = ['Unconstrained', 'R. Husk Availability', 'Transport Limit', 'Wood Pellet Capacity']
    technologies = ['Natural Gas', 'Wood Pellets'] + [f'R. Husk Zone {i}' for i in range(1, 6)]
    
    # Percentage values for each technology under different scenarios
    data = {
        'Scenario': scenarios,
        'Natural Gas': [0.0, 0.0, 0.0, 52.2],
        'Wood Pellets': [0.0, 70.4, 83.1, 18.2],
        'R. Husk Zone 1': [100.0, 5.9, 5.9, 5.9],
        'R. Husk Zone 2': [0.0, 5.9, 5.9, 5.9],
        'R. Husk Zone 3': [0.0, 5.9, 5.1, 5.9],
        'R. Husk Zone 4': [0.0, 5.9, 0.0, 5.9],
        'R. Husk Zone 5': [0.0, 5.9, 0.0, 5.9],
        'GWP': [0.859, 0.919, 0.928, 1.264]
    }
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Set 'Scenario' as the index
    df.set_index('Scenario', inplace=True)
    
    # Prepare the DataFrame for plotting
    plot_data = df[technologies]
    
    # Colors: Define a cohesive color palette
    colors = ['#2E86C1', '#E67E22', '#1E8449', '#229954', '#27AE60', '#2ECC71', '#82E0AA']
    
    # Plotting
    fig, ax1 = plt.subplots(figsize=(8, 4))
    
    # Create a stacked bar plot
    plot_data.plot(kind='bar', stacked=True, ax=ax1, color=colors, edgecolor='black')
    
    # Set labels and title
    ax1.set_xlabel('Scenario', fontsize=12)
    ax1.set_ylabel('Percentage Allocation (%)', fontsize=12)
    ax1.set_ylim(0, 100)
    
    # Add percentage labels on each segment
    for idx, scenario in enumerate(df.index):
        cumulative = 0
        for tech_idx, tech in enumerate(technologies):
            value = df.loc[scenario, tech]
            if value > 0:
                height = value
                y = cumulative + height / 2
                ax1.text(idx, y, f'{value:.1f}%', ha='center', va='center', fontsize=9, color='white' if height > 15 else 'black')
                cumulative += height
    
    # Adjust x-axis labels
    ax1.set_xticklabels(df.index, rotation=0, fontsize=10)
    
    # Create a second y-axis for the GWP impact
    ax2 = ax1.twinx()
    ax2.plot(df.index, df['GWP'], color='red', marker='o', markeredgecolor='black', linestyle='', linewidth=2, label='GWP')
    ax2.set_ylabel('Global Warming Potential (GWP)', fontsize=12)
    ax2.set_ylim(0.8, 1.3)
    ax2.tick_params(axis='y', labelsize=10)
    
    # Adjust legend
    handles1, labels1 = ax1.get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(handles=handles1 + handles2, labels=labels1 + labels2, loc='upper center', bbox_to_anchor=(0.5, 1.28), ncol=4, fontsize=10)
    
    # Add gridlines
    ax1.grid(True, which='major', linestyle='--', linewidth=0.5, alpha=0.7)
    
    # Adjust layout
    plt.tight_layout()
    
    # Show the plot
    plt.show()




