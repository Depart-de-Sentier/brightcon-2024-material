import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import argrelextrema
from scipy.optimize import fsolve
from matplotlib.widgets import Slider

# Define the polynomial function with three minima
def f(x):
    return (x - 4) * (x + 2) * (x + 1) * (x + 4)

# Define the linear function for constraints
def linear_curve(x):
    return -20 * x - 50

def equation(x):
    return f(x) - linear_curve(x)

# Generate x values from -6 to 5
x = np.linspace(-6, 5, 1000)
y = f(x)
y_linear = linear_curve(x)

# Find local minima
local_min_indices = argrelextrema(y, np.less)[0]
local_min_x = x[local_min_indices]
local_min_y = y[local_min_indices]

# Identify the global minimum
global_min_index = np.argmin(y)
global_min_x = x[global_min_index]
global_min_y = y[global_min_index]

# Find crossing points
initial_guesses = [-5, -3, 0, 3]
crossing_points = fsolve(equation, initial_guesses)
crossing_y = f(crossing_points)

def create_slider_plot():
    """
    Create an interactive plot with a slider that lets you switch between different
    visualizations of the function.
    """
    fig, ax = plt.subplots(figsize=(6, 4))
    plt.subplots_adjust(bottom=0.25)

    # Initial plot
    [line] = ax.plot(x, y, label=r'$f(x) = (x - 4)(x + 2)(x + 1)(x + 4)$', color='#1f77b4', linewidth=2)
    ax.set_xlim([-6, 5])
    ax.set_ylim([min(y) * 1.2, max(y) * 1.05])
    ax.set_xlabel('x', fontsize=14)
    ax.set_ylabel('f(x)', fontsize=14)
    ax.legend(loc='best', fontsize=12)
    ax.grid(True)

    # Create the slider for switching between plots
    ax_slider = plt.axes([0.25, 0.1, 0.5, 0.03], facecolor='lightgoldenrodyellow')
    slider = Slider(ax_slider, 'Plot', 1, 7, valinit=1, valstep=1)

    def update(val):
        plot_type = int(slider.val)
        ax.clear()

        if plot_type == 1:
            ax.plot(x, y, label=r'$f(x) = (x - 4)(x + 2)(x + 1)(x + 4)$', color='#1f77b4', linewidth=2)
            ax.set_title('Polynomial Objective Function without Constraints')

        elif plot_type == 2:
            ax.plot(x, y, label=r'$f(x) = (x - 4)(x + 2)(x + 1)(x + 4)$', color='#1f77b4', linewidth=2)
            ax.plot(local_min_x, local_min_y, 'ro', markersize=8, markeredgecolor='darkred', markeredgewidth=2, label='Local Minimum')
            ax.plot(global_min_x, global_min_y, 'bo', markersize=10, markeredgecolor='darkblue', markeredgewidth=2, label='Global Minimum')
            ax.set_title('Location of Minima')

        elif plot_type == 3:
            ax.plot(x, y, label=r'$f(x) = (x - 4)(x + 2)(x + 1)(x + 4)$', color='#1f77b4', linewidth=2)
            ax.axvline(x=-5, color='red', linestyle='--', linewidth=1.5)
            ax.axvline(x=4, color='red', linestyle='--', linewidth=1.5)
            ax.fill_between(x, min(y) * 1.2, max(y) * 1.05, where=(x >= -6) & (x <= -5), color='red', alpha=0.1)
            ax.fill_between(x, min(y) * 1.2, max(y) * 1.05, where=(x >= 4) & (x <= 5), color='red', alpha=0.1)
            ax.plot(local_min_x, local_min_y, 'ro', markersize=8, markeredgecolor='darkred', markeredgewidth=2, label='Local Minimum')
            ax.plot(global_min_x, global_min_y, 'bo', markersize=10, markeredgecolor='darkblue', markeredgewidth=2, label='Global Minimum')
            ax.set_title('Adding inequality constraints')

        elif plot_type == 4:
            ax.plot(x, y, label=r'$f(x) = (x - 4)(x + 2)(x + 1)(x + 4)$', color='#1f77b4', linewidth=2)
            ax.axvline(x=-5, color='red', linestyle='--', linewidth=1.5)
            ax.axvline(x=-1, color='red', linestyle='--', linewidth=1.5)
            ax.fill_between(x, min(y) * 1.2, max(y) * 1.05, where=(x >= -6) & (x <= -5), color='red', alpha=0.1)
            ax.fill_between(x, min(y) * 1.2, max(y) * 1.05, where=(x >= -1) & (x <= 5), color='red', alpha=0.1)
            ax.plot(local_min_x, local_min_y, 'rx', markersize=7, markeredgecolor='darkred', markeredgewidth=2, label='Infeasible Minimum')
            ax.plot(local_min_x[0], local_min_y[0], 'bo', markersize=10, markeredgecolor='darkblue', markeredgewidth=2, label='Global Minimum')
            ax.set_title('Indicating new Minima')

        elif plot_type == 5:
            ax.plot(x, y, label=r'$f(x) = (x - 4)(x + 2)(x + 1)(x + 4)$', color='#1f77b4', linewidth=2)
            ax.axvline(x=-5, color='red', linestyle='--', linewidth=1.5)
            ax.axvline(x=1, color='red', linestyle='--', linewidth=1.5)
            ax.fill_between(x, min(y) * 1.2, max(y) * 1.05, where=(x >= -6) & (x <= -5), color='red', alpha=0.1)
            ax.fill_between(x, min(y) * 1.2, max(y) * 1.05, where=(x >= 1) & (x <= 5), color='red', alpha=0.1)
            ax.plot(local_min_x[1], local_min_y[1], 'rx', markersize=7, markeredgecolor='darkred', markeredgewidth=2, label='Infeasible Minimum')
            ax.plot(local_min_x[0], local_min_y[0], 'ro', markersize=7, markeredgecolor='darkred', markeredgewidth=2, label='Local Minimum')
            ax.plot(1, f(1), 'bo', markersize=10, markeredgecolor='darkblue', markeredgewidth=2, label='Global Minimum')
            ax.set_title('Minima can be located on the Edges')

        elif plot_type == 6:
            ax.plot(x, y, label=r'$f(x) = (x - 4)(x + 2)(x + 1)(x + 4)$', color='#1f77b4', linewidth=2)
            ax.plot(x, y_linear, label=r'$h(x) = -20x - 50$', color='orange', linestyle='--', linewidth=2)
            ax.axvline(x=-5, color='red', linestyle='--', linewidth=1.5)
            ax.axvline(x=4, color='red', linestyle='--', linewidth=1.5)
            ax.fill_between(x, min(y) * 1.2, max(y) * 1.05, where=(x >= -6) & (x <= -5), color='red', alpha=0.1)
            ax.fill_between(x, min(y) * 1.2, max(y) * 1.05, where=(x >= 4) & (x <= 5), color='red', alpha=0.1)
            ax.set_title('Adding an Equality Constraint')

        elif plot_type == 7:
            ax.plot(x, y, label=r'$f(x) = (x - 4)(x + 2)(x + 1)(x + 4)$', color='#1f77b4', linewidth=2)
            ax.plot(x, y_linear, label=r'$g(x) = -20x - 50$', color='orange', linestyle='--', linewidth=2)
            ax.axvline(x=-5, color='red', linestyle='--', linewidth=1.5)
            ax.axvline(x=4, color='red', linestyle='--', linewidth=1.5)
            ax.fill_between(x, min(y) * 1.2, max(y) * 1.05, where=(x >= -6) & (x <= -5), color='red', alpha=0.1)
            ax.fill_between(x, min(y) * 1.2, max(y) * 1.05, where=(x >= 4) & (x <= 5), color='red', alpha=0.1)
            ax.plot(crossing_points, crossing_y, 'ro', markersize=7, markeredgecolor='purple', markeredgewidth=2, label='Feasible Points')
            ax.plot(crossing_points[3], crossing_y[3], 'bo', markersize=10, markeredgecolor='darkblue', markeredgewidth=2, label='Global Minimum')
            ax.set_title('Indicating new Feasible Points and Minima')

        # Set common elements for the plot
        ax.set_xlim([-6, 5])
        ax.set_ylim([min(y) * 1.2, max(y) * 1.05])
        ax.set_xlabel('x', fontsize=14)
        ax.set_ylabel('f(x)', fontsize=14)
        ax.legend(loc='best', fontsize=12)
        ax.grid(True)

        fig.canvas.draw_idle()

    # Attach the update function to the slider
    slider.on_changed(update)

    # Show the initial plot
    plt.show()
