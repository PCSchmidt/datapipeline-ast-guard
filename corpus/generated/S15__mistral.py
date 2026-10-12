import pandas as pd

# Sample lookup table (replace this with your actual data)
lookup = pd.DataFrame({
    'event_id': [1, 2, 3, 4],
    'attribute': ['A', 'B', 'C', 'D'],
    'value': [10, 20, 30, 40]
})

# Sample events stream (replace this with your actual data)
events = [
    {'id': 1, 'type': 'event_A'},
    {'id': 2, 'type': 'event_B'},
    {'id': 3, 'type': 'event_C'},
    {'id': 4, 'type': 'event_D'},
    {'id': 5, 'type': 'event_E'},
]

# Enrich events with lookup table attributes
enriched_events = pd.concat([
    lookup.loc[lookup['event_id'].isin(events[:, 0]), :],
    pd.DataFrame(events, columns=['id', 'type']).merge(lookup[['attribute', 'value']], on='event_id', how='left')
], axis=1)

print(enriched_events)
