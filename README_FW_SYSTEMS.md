# Faction Warfare Systems Filtering

This set of scripts is designed to filter the original solar systems pickle file to extract only the Faction Warfare systems for each warzone and save them to separate pickle files. This approach avoids the infinite loop issue that was occurring with the previous graph visualization implementation.

## Scripts

### 1. `filter_fw_systems.py`

This script filters the original pickle file to extract only the Faction Warfare systems for each warzone and saves them to separate pickle files:

- `ama_min.pickle`: Contains systems for the Amarr-Minmatar warzone
- `cal_gal.pickle`: Contains systems for the Caldari-Gallente warzone

The filtering is done based on:
- Region names associated with each warzone
- Permanent frontline systems defined in the codebase
- Connected systems to ensure the graph is complete

Usage:
```bash
python filter_fw_systems.py
```

### 2. `examine_filtered_pickles.py`

This script examines the filtered pickle files to verify they contain the expected data. It provides statistics and sample data from each warzone.

Usage:
```bash
python examine_filtered_pickles.py
```

### 3. `update_web_visualizer.py`

This script updates the web visualizer to use the filtered pickle files instead of the original one. It modifies:
- `app.py`: Updates the imports and the `get_graph_data` function to use the appropriate pickle file based on the selected warzone.

Usage:
```bash
python update_web_visualizer.py
```

## Implementation Details

### Filtering Approach

1. **Region-based filtering**: Systems are initially filtered based on the regions they belong to.
2. **Permanent frontlines**: Systems defined as permanent frontlines in the codebase are included.
3. **Connected systems**: All systems connected to the filtered systems are included to ensure the graph is complete.

### Benefits

1. **Reduced data size**: The filtered pickle files are much smaller than the original one, which improves performance.
2. **Focused visualization**: The graph only shows systems relevant to each warzone.
3. **Avoids infinite loops**: By pre-filtering the systems, we avoid the infinite loop issue that was occurring with the previous implementation.

## Next Steps

After running these scripts:

1. Verify that the filtered pickle files contain the expected data using `examine_filtered_pickles.py`.
2. Test the web visualizer to ensure it correctly displays the graph for each warzone.
3. Consider further optimizations to the graph visualization, such as:
   - Improving the layout algorithm
   - Adding more filtering options
   - Enhancing the visual representation of system attributes

