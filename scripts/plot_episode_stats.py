import matplotlib.pyplot as plt
import numpy as np
from statistics import mean, mode, stdev
from typing import List, Dict, Union
def plot(control_stats,episode_stats):
  #{'timesteps': 55, 
  # 'ants_eaten': {'soldier': 1, 'scout': 1, 'runner': 0}, 
  # 'food_eaten': {'soldier': 3, 'scout': 2, 'runner': 1}, 'inference_time_mean': np.float64(0.048017586125327104), 
  # 'inference_time_range': [{'soldier': 1, 'scout': 1, 'runner': 0}, {'soldier': 1, 'scout': 1, 'runner': 0}], 
  # 'num_ants_alive': 3}

  # for mean, mode, and range
    #plot ants eaten, compare with control
      #im thinking bar chart with a bar per species and paired with its control
    #plot food eaten, compare with control
      #im thinking bar chart with a bar per species and paired with its control

  for method in ['mean','mode','range','std']:
      
    control_stats_agg=aggregate_dicts([{k:v for k,v in d.items() if k in ['ants_eaten','food_eaten']} for d in control_stats],method=method)
    episode_stats_agg=aggregate_dicts([{k:v for k,v in d.items() if k in ['ants_eaten','food_eaten']} for d in episode_stats],method=method)
    plot_side_by_side_bars(control_stats_agg,episode_stats_agg,f'{method}_Comparison')


def plot_side_by_side_bars(dict1, dict2, title="Comparison", xlabel="Keys", ylabel="Values"):
    """
    Create a side-by-side bar chart for two dictionaries with matching keys.

    Parameters:
        dict1 (dict): First dictionary with keys and values.
        dict2 (dict): Second dictionary with keys and values.
        title (str): Title of the chart. Default is "Comparison Chart".
        xlabel (str): Label for the x-axis. Default is "Keys".
        ylabel (str): Label for the y-axis. Default is "Values".
    """
    if set(dict1.keys()) != set(dict2.keys()):
        raise ValueError("The keys of both dictionaries must match.")

    keys = list(dict1.keys())
    values1 = [dict1[key] for key in keys]
    values2 = [dict2[key] for key in keys]

    x = np.arange(len(keys))  # the label locations
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots(figsize=(10, 6))
    rects1 = ax.bar(x - width/2, values1, width, label='Dict 1')
    rects2 = ax.bar(x + width/2, values2, width, label='Dict 2')

    # Add some text for labels, title, and custom x-axis tick labels, etc.
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.set_xticks(x)
    ax.set_xticklabels(keys)
    ax.legend()

    # Add labels to each bar
    ax.bar_label(rects1, padding=3)
    ax.bar_label(rects2, padding=3)

    fig.tight_layout()
    plt.show()
    plt.savefig('./figures/title.png')


def aggregate_dicts(dict_list: List[Dict[str, Union[int, float]]], method: str) -> Dict[str, Union[int, float]]:
    """
    Aggregates the values of a list of dictionaries by their keys using a specified method.

    Parameters:
        dict_list (List[Dict[str, Union[int, float]]]): List of dictionaries with numeric values.
        method (str): Aggregation method - 'mean', 'mode', 'range', or 'std' (standard deviation).

    Returns:
        Dict[str, Union[int, float]]: A dictionary with aggregated values.
    """
    if not dict_list:
        raise ValueError("The list of dictionaries is empty.")

    # Ensure all dictionaries have the same keys
    keys = set(dict_list[0].keys())
    for d in dict_list:
        if set(d.keys()) != keys:
            raise ValueError("All dictionaries must have the same keys.")

    # Aggregate values for each key
    aggregated_dict = {}
    for key in keys:
        values = [d[key] for d in dict_list]

        if method == 'mean':
            aggregated_dict[key] = mean(values)
        elif method == 'mode':
            try:
                aggregated_dict[key] = mode(values)
            except:
                aggregated_dict[key] = None  # If no mode exists
        elif method == 'range':
            aggregated_dict[key] = max(values) - min(values)
        elif method == 'std':
            if len(values) > 1:
                aggregated_dict[key] = stdev(values)
            else:
                aggregated_dict[key] = 0  # Standard deviation is 0 for a single value
        else:
            raise ValueError("Invalid method. Choose 'mean', 'mode', 'range', or 'std'.")

    return aggregated_dict
