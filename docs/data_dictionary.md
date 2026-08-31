# OPTIMA-X Phase 1 Data Dictionary

| Entity | Field | Type | Meaning | Availability | Validation |
|---|---|---|---|---|---|
| Order | `order_id` | string | Unique order identifier | Creation | Required, unique |
| Order | `pickup` | node/location | Origin node or coordinates | Creation | Must map to graph |
| Order | `destination` | node/location | Delivery node or coordinates | Creation | Must map to graph |
| Order | `demand_units` | non-negative integer | Capacity consumed | Creation | Greater than zero |
| Order | `priority` | integer | Dispatch priority | Creation | Bounded configured range |
| Order | `created_at` | UTC datetime | Order creation time | Creation | Timezone-aware |
| Order | `time_window` | interval | Earliest and latest delivery time | Creation | End after start |
| Vehicle | `vehicle_id` | string | Unique vehicle identifier | Scenario start | Required, unique |
| Vehicle | `capacity_units` | non-negative integer | Maximum load | Scenario start | Greater than zero |
| Vehicle | `current_location` | node/location | Current vehicle position | Decision time | Must map to graph |
| Vehicle | `available_from` | UTC datetime | Shift start | Scenario start | Before shift end |
| Vehicle | `available_until` | UTC datetime | Shift end | Scenario start | After shift start |
| Node | `node_id` | string | Road-network vertex | Graph build | Unique |
| Node | `latitude` | float | WGS84 latitude or normalized coordinate | Graph build | -90 to 90 |
| Node | `longitude` | float | WGS84 longitude or normalized coordinate | Graph build | -180 to 180 |
| Edge | `source` | string | Origin node | Graph build | Existing node |
| Edge | `target` | string | Destination node | Graph build | Existing node |
| Edge | `distance_km` | non-negative float | Road segment distance | Graph build | Non-negative |
| Edge | `travel_time_min` | non-negative float | Base travel time | Graph build | Positive for traversable edge |
| Edge | `cost` | non-negative float | Routing objective weight | Decision time | Non-negative |
| Traffic | `timestamp` | UTC datetime | Traffic observation time | Decision time | Ordered |
| Traffic | `zone_id` | string | Traffic zone | Decision time | Required |
| Traffic | `multiplier` | float | Dynamic cost multiplier | Decision time | Greater than zero |
| Weather | `timestamp` | UTC datetime | Weather observation time | Decision time | Ordered |
| Weather | `condition` | category | Weather state | Decision time | Controlled vocabulary |
| Trip | `actual_eta` | non-negative float | Observed travel duration | After delivery | Never negative |
| Decision | `scenario_id` | string | Reproducible scenario identifier | Decision time | Required |
| Decision | `algorithm` | string | Strategy used | Decision time | Registered strategy |

`actual_eta`, delivery time, and post-delivery outcome fields must never be used as features for a decision made before delivery. Raw files are immutable inputs; cleaned and processed outputs are derived artifacts with a recorded source manifest.
