import numpy as np
import matplotlib.pyplot as plt
from pyomo.environ import ConcreteModel, Var, Objective, Constraint, SolverFactory, NonNegativeReals, log, minimize, value

# Constants
T_h_in = 150  # °C, Inlet temperature of hot stream
T_c_in = 25   # °C, Inlet temperature of cold stream
T_h_out_target = 50  # °C, Target outlet temperature of hot stream
T_c_out_target = 200 # °C, Target outlet temperature of cold stream
C_h = 5000    # W/K, Heat capacity flow rate of hot stream
C_c = 3000    # W/K, Heat capacity flow rate of cold stream
U = 1000      # W/m^2K, Overall heat transfer coefficient
C_hot = 0.020 # $/W, Cost per unit energy of hot utility
C_cold = 0.015 # $/W, Cost per unit energy of cold utility
C_A = 1000    # $/m^2, Cost coefficient for heat exchanger area
n = 0.7       # Scaling exponent for heat exchanger cost

# Emission Factors
EF_hot = 0.06   # kg CO₂/W, Emission factor for the hot utility
EF_cold = 0.01  # kg CO₂/W, Emission factor for the cold utility
EF_A = 50       # kg CO₂/m², Emission factor for the heat exchanger area

def define_variables(model):
    model.T_h_out = Var(within=NonNegativeReals, bounds=(T_c_in, T_h_in))  # °C
    model.T_c_out = Var(within=NonNegativeReals, bounds=(T_c_in, T_h_in))  # °C
    model.Q = Var(within=NonNegativeReals, bounds=(0, 1e8))  # W, Heat transferred
    model.A = Var(within=NonNegativeReals, bounds=(0, 1000), initialize=1)  # m^2, Heat exchanger area

def define_constraints(model):
    model.EnergyBalance = Constraint(expr=model.Q == C_h * (T_h_in - model.T_h_out))
    model.EnergyBalanceCold = Constraint(expr=model.Q == C_c * (model.T_c_out - T_c_in))
    model.LMTD = Constraint(expr=model.Q == U * model.A * ((T_h_in - model.T_c_out) - (model.T_h_out - T_c_in)) / log((T_h_in - model.T_c_out) / (model.T_h_out - T_c_in)))

def solve_pareto_front(steps=50):
    costs = []
    emissions = []
    weights = np.linspace(0, 1, steps)

    for w in weights:
        model = ConcreteModel()

        # Define variables and constraints
        define_variables(model)
        define_constraints(model)

        # Define weighted objective
        def weighted_objective_rule(model):
            # Economic Objective: Total Cost
            cost_utilities = C_h * (model.T_h_out - T_h_out_target) * C_hot + C_c * (T_c_out_target - model.T_c_out) * C_cold
            cost_HX = C_A * (model.A) ** n
            total_cost = cost_utilities + cost_HX

            # Environmental Objective: Total Emissions
            emissions_utilities = EF_hot * C_h * (model.T_h_out - T_h_out_target) + EF_cold * C_c * (T_c_out_target - model.T_c_out)
            emissions_HX = EF_A * model.A
            total_emissions = emissions_utilities + emissions_HX

            # Weighted sum of both objectives
            return w * total_cost + (1 - w) * total_emissions

        model.WeightedObjective = Objective(rule=weighted_objective_rule, sense=minimize)

        # Solve the model
        solver = SolverFactory('ipopt')
        result = solver.solve(model, tee=False)

        if result.solver.termination_condition == 'optimal':
            # Calculate cost and emissions after solving
            cost_utilities = value(C_h * (model.T_h_out - T_h_out_target) * C_hot + C_c * (T_c_out_target - model.T_c_out) * C_cold)
            cost_HX = value(C_A * (model.A) ** n)
            total_cost = cost_utilities + cost_HX

            emissions_utilities = value(EF_hot * C_h * (model.T_h_out - T_h_out_target) + EF_cold * C_c * (T_c_out_target - model.T_c_out))
            emissions_HX = value(EF_A * model.A)
            total_emissions = emissions_utilities + emissions_HX

            # Store the objectives for the Pareto front
            costs.append(total_cost)
            emissions.append(total_emissions)

    return np.array(costs), np.array(emissions)

def plot_pareto_front(costs, emissions):
    # Set a fixed white background for the plot
    plt.figure(figsize=(5, 3), facecolor='white')

    # Plot the Pareto front
    plt.plot(emissions, costs, '-o', color='#1f77b4', markeredgecolor='darkblue', label='Pareto Front')

    # Find the anchor points (minimum cost and minimum emissions)
    min_cost_index = np.argmin(costs)
    min_emission_index = np.argmin(emissions)

    # Plot anchor points with larger markers and distinct colors
    plt.plot(emissions[min_cost_index], costs[min_cost_index], 'go', markersize=10, markeredgecolor='darkgreen', label='Minimum Cost')
    plt.plot(emissions[min_emission_index], costs[min_emission_index], 'ro', markersize=10, markeredgecolor='darkred', label='Minimum Emissions')

    # Plot the utopian point (0 emissions, minimum cost)
    utopian_emissions = min(emissions)
    utopian_cost = min(costs)
    plt.plot(utopian_emissions, utopian_cost, 'yo', markersize=10, markeredgecolor='darkgoldenrod', label='Utopian Point')

    # Labels and title in black for light theme
    plt.xlabel('Total Emissions [kg CO₂]', fontsize=12, color='black')
    plt.ylabel('Total Cost [$]', fontsize=12, color='black')

    # Set grid style
    plt.grid(True, linestyle='--', color='gray', alpha=0.7)

    # Set axis limits and tick colors
    plt.gca().spines['bottom'].set_color('black')
    plt.gca().spines['top'].set_color('black')
    plt.gca().spines['right'].set_color('black')
    plt.gca().spines['left'].set_color('black')
    
    plt.gca().xaxis.label.set_color('black')
    plt.gca().yaxis.label.set_color('black')
    plt.gca().tick_params(colors='black')
    plt.gca().title.set_color('black')

    # Set the legend with a white background
    legend = plt.legend(
        fontsize=10, 
        facecolor='white',  # Explicit white background for legend
        edgecolor='black',  # Black border for clarity
        loc='center left', 
        bbox_to_anchor=(0.44, 0.73),
        framealpha=1  # Fully opaque
    )
    
    # Ensure the legend text is black
    for text in legend.get_texts():
        text.set_color('black')

    # Show the plot
    plt.show()
    

def plot_cost_tradeoff(x, investment_cost, operating_cost, combined_cost):
    # Set a fixed white background for the plot
    plt.figure(figsize=(5, 3), facecolor='white')
    
    # Plot the costs with specific colors for each cost component
    plt.plot(x, investment_cost, label='Investment Cost', color='#1f77b4')  # Blue for investment cost
    plt.plot(x, operating_cost, label='Operating Cost', color='#ff7f0e')    # Orange for operating cost
    plt.plot(x, combined_cost, label='Combined Cost', color='#2ca02c', linestyle='--')  # Green for combined cost

    # Highlight the minimum point of the combined cost
    min_index = np.argmin(combined_cost)
    plt.plot(x[min_index], combined_cost[min_index], 'ro', label='Optimum')

    # Labels and title in black for light theme
    plt.xlabel('Degree of Integration', fontsize=12, color='black')
    plt.ylabel('Cost', fontsize=12, color='black')

    # Set the grid with dashed lines for better readability
    plt.grid(True, linestyle='--', color='gray', alpha=0.7)

    # Set axis limits and tick colors
    plt.gca().spines['bottom'].set_color('black')
    plt.gca().spines['top'].set_color('black')
    plt.gca().spines['right'].set_color('black')
    plt.gca().spines['left'].set_color('black')
    
    plt.gca().xaxis.label.set_color('black')
    plt.gca().yaxis.label.set_color('black')
    plt.gca().tick_params(colors='black')
    plt.gca().title.set_color('black')

    # Set the legend in black text
    legend = plt.legend(
        fontsize=10, 
        facecolor='white',  # Explicit white background for legend
        edgecolor='black',  # Black border for clarity
        loc='center left', 
        bbox_to_anchor=(0.54, 0.33)
    )
    for text in legend.get_texts():
        text.set_color('black')

    # Show the plot with a fixed white background
    plt.show()