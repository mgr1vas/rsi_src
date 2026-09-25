# Data quality model

The current canonical dataset is derived from journalistic reporting and geocoding.
It does **not** contain official police crash coordinates.

Key meanings:

- `coordinate_quality`: pipeline quality indicator, not an exact-location probability.
- `marker_radius_m`: visualization uncertainty, not a safety/risk radius.
- `verified_officially`: `false` for current records.
- `usable_for_map`: passed current checks for approximate map display.
- `usable_for_safety_warning`: `false` for all current journalism-derived rows.

Rejected records stay in `data/qa/rejected_review.json` so future improvements can
recover them rather than silently discarding them.
