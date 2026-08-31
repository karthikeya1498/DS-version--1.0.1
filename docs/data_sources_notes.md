# Verified dataset-source notes

## OpenStreetMap

The OpenStreetMap Foundation states that raw OSM data can be downloaded for a defined area, country, region, or feature type such as roads. OPTIMA-X will use a bounded extract for reproducible graph experiments and preserve OSM attribution in the manifest. Source: https://welcome.openstreetmap.org/working-with-osm-data/downloading-and-using/

## NYC TLC Trip Record Data

The NYC Taxi and Limousine Commission publishes yellow, green, FHV, and HVFHV records. The official page documents pickup/drop-off timestamps and locations, trip distance, and related trip fields. It states that trip records are published monthly and are stored in Parquet because of their size. OPTIMA-X will use a bounded month as a mobility/traffic proxy and derive zone-time demand and travel-time aggregates rather than treating the records as direct delivery orders. Source: https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page

## Dataset integration decision

The unified ecosystem uses OSM for graph topology, NYC TLC for trip-derived traffic and zone demand, UCI Bike Sharing for a compact hourly forecasting benchmark, NOAA/Meteostat for weather covariates, a public holiday calendar for event indicators, and synthetic fleet records. Raw files remain separate and are joined only in processed tables with source manifests.
