"""SmartRoute Pro — Interactive Streamlit Dashboard.

Features:
  - Interactive Folium map with depot/destination markers
  - Upload CSV or use demo data
  - Choose optimization algorithm and parameters
  - Real-time route visualization on map
  - Fleet analytics with charts
  - Algorithm comparison
  - ML demand forecast visualization
  - Export optimized routes
"""

import io
import json
import sys
from pathlib import Path

import folium
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from streamlit_folium import st_folium

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.tsp_solver import ALGORITHMS
from app.core.vrp_engine import VRPEngine
from app.services.data_loader import (
    export_routes_csv,
    generate_demo_data,
    parse_csv_upload,
)
from app.services.geocoding import geocode

# ---------------------------------------------------------------------------
# Page Config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="SmartRoute Pro",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #888;
        margin-top: -10px;
        margin-bottom: 20px;
    }
    .metric-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Color palette for routes
# ---------------------------------------------------------------------------
ROUTE_COLORS = [
    "#e6194b", "#3cb44b", "#4363d8", "#f58231", "#911eb4",
    "#42d4f4", "#f032e6", "#bfef45", "#fabed4", "#469990",
    "#dcbeff", "#9A6324", "#800000", "#aaffc3", "#808000",
    "#000075", "#a9a9a9", "#e6beff", "#ffe119", "#000000",
]


def get_color(idx: int) -> str:
    return ROUTE_COLORS[idx % len(ROUTE_COLORS)]


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown('<p class="main-header">SmartRoute Pro</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">AI-Driven Route Optimization</p>', unsafe_allow_html=True)
    st.divider()

    # Data source
    st.subheader("📍 Data Source")
    data_source = st.radio(
        "Choose data source:",
        ["Demo Data", "Upload CSV", "Enter Coordinates"],
        label_visibility="collapsed",
    )

    destinations = None
    depots = None

    if data_source == "Demo Data":
        n_dest = st.slider("Number of destinations", 20, 500, 100, 10)
        n_deps = st.slider("Number of depots", 2, 15, 5)
        center_lat = st.number_input("Center latitude", value=48.8566, format="%.4f")
        center_lon = st.number_input("Center longitude", value=2.3522, format="%.4f")
        destinations, depots = generate_demo_data(n_dest, n_deps, center_lat, center_lon)

    elif data_source == "Upload CSV":
        st.info("CSV must have 'lat' and 'lon' columns")
        dest_file = st.file_uploader("Destinations CSV", type=["csv"], key="dest_upload")
        depot_file = st.file_uploader("Depots CSV", type=["csv"], key="depot_upload")

        if dest_file and depot_file:
            try:
                destinations = parse_csv_upload(dest_file.getvalue().decode())
                depots = parse_csv_upload(depot_file.getvalue().decode())
                st.success(f"Loaded {len(destinations)} destinations, {len(depots)} depots")
            except Exception as e:
                st.error(f"Error parsing CSV: {e}")

    elif data_source == "Enter Coordinates":
        st.info("Enter depot and destination coordinates (one per line: lat, lon)")

        depot_text = st.text_area(
            "Depots (lat, lon per line):",
            "48.8566, 2.3522\n49.0549, 1.2596\n48.5528, 2.4901",
            height=100,
        )
        dest_text = st.text_area(
            "Destinations (lat, lon per line):",
            "48.88, 2.35\n49.05, 2.35\n48.70, 2.10\n49.20, 2.60\n48.50, 2.80\n48.95, 1.80\n49.10, 2.20\n48.60, 2.50\n49.30, 2.40\n48.40, 2.30",
            height=150,
        )

        try:
            depots = np.array([[float(x.strip()) for x in line.split(",")] for line in depot_text.strip().split("\n") if line.strip()])
            destinations = np.array([[float(x.strip()) for x in line.split(",")] for line in dest_text.strip().split("\n") if line.strip()])
        except Exception:
            st.error("Invalid coordinate format. Use: lat, lon")

    # Geocoding
    st.divider()
    st.subheader("🔍 Geocode Address")
    address = st.text_input("Enter address:", placeholder="e.g., Eiffel Tower, Paris")
    if address:
        result = geocode(address)
        if result:
            lat, lon, display = result
            st.success(f"📍 {lat:.4f}, {lon:.4f}")
            st.caption(display)
        else:
            st.warning("Address not found")

    st.divider()

    # Algorithm settings
    st.subheader("⚙️ Optimization Settings")
    algorithm = st.selectbox(
        "TSP Algorithm",
        list(ALGORITHMS.keys()),
        index=3,
        format_func=lambda x: ALGORITHMS[x],
    )

    clustering = st.selectbox("Clustering Method", ["kmeans", "nearest"])

    with st.expander("Advanced Settings"):
        vehicle_cap = st.number_input("Vehicle capacity (kg)", 500, 10000, 2000, 100)
        max_stops = st.slider("Max stops per vehicle", 5, 100, 50)
        near_thresh = st.slider("Near threshold (km)", 10, 100, 40)
        use_forecast = st.checkbox("ML demand forecasting", value=True)

    run_btn = st.button("🚀 Optimize Routes", type="primary", use_container_width=True)
    compare_btn = st.button("📊 Compare All Algorithms", use_container_width=True)


# ---------------------------------------------------------------------------
# Main Content Area
# ---------------------------------------------------------------------------
st.markdown('<p class="main-header">SmartRoute Pro</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">AI-Driven Multi-Depot Vehicle Route Optimization with ML Demand Forecasting</p>', unsafe_allow_html=True)

if destinations is None or depots is None:
    st.info("👈 Configure data and settings in the sidebar, then click **Optimize Routes**.")
    st.stop()

# ---------------------------------------------------------------------------
# OPTIMIZATION
# ---------------------------------------------------------------------------
if run_btn:
    with st.spinner(f"Optimizing with {ALGORITHMS[algorithm]}..."):
        engine = VRPEngine(algorithm=algorithm)
        result = engine.optimize(
            destinations=destinations,
            depots=depots,
            clustering_method=clustering,
            vehicle_capacity=vehicle_cap,
            max_per_vehicle=max_stops,
            near_threshold_km=near_thresh,
            use_demand_forecast=use_forecast,
        )
    st.session_state["result"] = result
    st.session_state["summary"] = result.summary()

if compare_btn:
    with st.spinner("Running all 4 algorithms for comparison..."):
        engine = VRPEngine()
        comparison = engine.compare_algorithms(destinations, depots)
    st.session_state["comparison"] = comparison

# ---------------------------------------------------------------------------
# Display Results
# ---------------------------------------------------------------------------
if "result" in st.session_state:
    result = st.session_state["result"]
    summary = st.session_state["summary"]

    # === Metrics Row ===
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    fc = summary["fleet_cost"]
    col1.metric("🚚 Vehicles", fc["total_vehicles"])
    col2.metric("📍 Stops", fc["total_stops"])
    col3.metric("📏 Distance", f"{fc['total_distance_km']:,.0f} km")
    col4.metric("⛽ Fuel", f"{fc['total_fuel_liters']:,.0f} L")
    col5.metric("💰 Cost", f"${fc['total_fuel_cost_usd']:,.0f}")
    col6.metric("🌱 CO₂", f"{fc['total_co2_kg']:,.0f} kg")

    st.caption(f"⏱️ Optimized in {summary['optimization_time_seconds']:.2f}s using **{ALGORITHMS[summary['algorithm']]}**")
    st.divider()

    # === Tabs ===
    tab_map, tab_analytics, tab_demand, tab_routes, tab_export = st.tabs(
        ["🗺️ Route Map", "📊 Analytics", "🤖 Demand Forecast", "📋 Route Details", "📥 Export"]
    )

    # --- TAB 1: Map ---
    with tab_map:
        center_lat = float(depots[:, 0].mean())
        center_lon = float(depots[:, 1].mean())
        m = folium.Map(location=[center_lat, center_lon], zoom_start=8, tiles="CartoDB positron")

        # Destination markers
        for i, dest in enumerate(destinations):
            folium.CircleMarker(
                location=[float(dest[0]), float(dest[1])],
                radius=3,
                color="#888",
                fill=True,
                fill_opacity=0.5,
                tooltip=f"Dest {i}",
            ).add_to(m)

        # Depot markers
        for i, depot in enumerate(depots):
            folium.Marker(
                location=[float(depot[0]), float(depot[1])],
                popup=f"Depot {i}",
                tooltip=f"🏭 Depot {i}",
                icon=folium.Icon(color="red", icon="warehouse", prefix="fa"),
            ).add_to(m)

        # Route lines
        for route in result.routes:
            color = get_color(route.vehicle_id)
            depot = route.depot_location
            points = [[float(depot[0]), float(depot[1])]]
            for wp in route.waypoints:
                points.append([float(wp[0]), float(wp[1])])
            points.append([float(depot[0]), float(depot[1])])  # return

            folium.PolyLine(
                points,
                color=color,
                weight=3,
                opacity=0.75,
                tooltip=f"Vehicle {route.vehicle_id} ({route.vehicle_type}) - {route.distance_km:.1f}km",
            ).add_to(m)

        st_folium(m, width=None, height=600)

    # --- TAB 2: Analytics ---
    with tab_analytics:
        col_a, col_b = st.columns(2)

        with col_a:
            # Distance by vehicle
            route_data = pd.DataFrame([r.cost.to_dict() for r in result.routes])
            fig_dist = px.bar(
                route_data,
                x="vehicle_id",
                y="distance_km",
                color="vehicle_type",
                title="Distance by Vehicle",
                color_discrete_sequence=["#667eea", "#f58231"],
            )
            st.plotly_chart(fig_dist)

        with col_b:
            # Cost breakdown pie
            fig_cost = px.pie(
                route_data,
                values="fuel_cost_usd",
                names=route_data.apply(lambda r: f"V{r['vehicle_id']} ({r['vehicle_type']})", axis=1),
                title="Fuel Cost Distribution",
                color_discrete_sequence=px.colors.qualitative.Set3,
            )
            st.plotly_chart(fig_cost)

        col_c, col_d = st.columns(2)

        with col_c:
            # CO2 by vehicle type
            co2_by_type = route_data.groupby("vehicle_type")[["co2_kg"]].sum().reset_index()
            fig_co2 = px.bar(
                co2_by_type,
                x="vehicle_type",
                y="co2_kg",
                title="CO₂ Emissions by Vehicle Type",
                color="vehicle_type",
                color_discrete_sequence=["#42d4f4", "#e6194b"],
            )
            st.plotly_chart(fig_co2)

        with col_d:
            # Stops per depot
            depot_stops = route_data.groupby("depot_id")[["num_stops"]].sum().reset_index()
            fig_stops = px.bar(
                depot_stops,
                x="depot_id",
                y="num_stops",
                title="Stops per Depot",
                color_discrete_sequence=["#764ba2"],
            )
            st.plotly_chart(fig_stops)

        # Efficiency metrics
        st.subheader("Efficiency Metrics")
        eff_col1, eff_col2, eff_col3, eff_col4 = st.columns(4)
        eff_col1.metric("Avg km/stop", f"{fc['total_distance_km'] / max(fc['total_stops'], 1):.1f}")
        eff_col2.metric("Avg stops/vehicle", f"{fc['total_stops'] / max(fc['total_vehicles'], 1):.1f}")
        eff_col3.metric("Avg hours/vehicle", f"{fc['total_time_hours'] / max(fc['total_vehicles'], 1):.1f}")
        eff_col4.metric("CO₂/km", f"{fc['total_co2_kg'] / max(fc['total_distance_km'], 1) * 1000:.0f} g")

    # --- TAB 3: Demand Forecast ---
    with tab_demand:
        if summary.get("demand_forecast"):
            dm = summary["demand_forecast"]
            st.success(f"ML Model R² Score: **{dm['cv_r2_mean']:.3f}** (±{dm['cv_r2_std']:.3f})")

            # Feature importance
            fi = dm.get("feature_importances", {})
            if fi:
                fi_df = pd.DataFrame(
                    {"Feature": list(fi.keys()), "Importance": list(fi.values())}
                ).sort_values("Importance", ascending=True)

                fig_fi = px.bar(
                    fi_df,
                    x="Importance",
                    y="Feature",
                    orientation="h",
                    title="Demand Prediction — Feature Importances",
                    color="Importance",
                    color_continuous_scale="Viridis",
                )
                st.plotly_chart(fig_fi)

            # Demand heatmap — use result.destinations to ensure length matches predictions
            if result.demand_predictions is not None:
                demand_df = pd.DataFrame({
                    "lat": result.destinations[:, 0],
                    "lon": result.destinations[:, 1],
                    "predicted_demand": result.demand_predictions,
                })
                fig_demand = px.scatter_map(
                    demand_df,
                    lat="lat",
                    lon="lon",
                    color="predicted_demand",
                    size="predicted_demand",
                    color_continuous_scale="YlOrRd",
                    zoom=7,
                    map_style="carto-positron",
                    title="Predicted Demand Heatmap",
                    height=500,
                )
                st.plotly_chart(fig_demand)
        else:
            st.info("Enable ML demand forecasting in settings and re-run optimization.")

    # --- TAB 4: Route Details ---
    with tab_routes:
        for route in result.routes:
            with st.expander(
                f"🚚 Vehicle {route.vehicle_id} | Depot {route.depot_id} | "
                f"{route.vehicle_type.upper()} | {route.distance_km:.1f} km | "
                f"{len(route.waypoints)} stops"
            ):
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Distance", f"{route.distance_km:.1f} km")
                c2.metric("Fuel", f"{route.cost.fuel_liters:.1f} L")
                c3.metric("Cost", f"${route.cost.fuel_cost_usd:.2f}")
                c4.metric("CO₂", f"{route.cost.co2_kg:.1f} kg")

                wp_df = pd.DataFrame(route.waypoints, columns=["Latitude", "Longitude"])
                wp_df.index = wp_df.index + 1
                wp_df.index.name = "Stop"
                st.dataframe(wp_df, height=200)

    # --- TAB 5: Export ---
    with tab_export:
        col_e1, col_e2 = st.columns(2)
        with col_e1:
            csv_data = export_routes_csv(result.routes)
            st.download_button(
                "📥 Download Routes CSV",
                csv_data,
                "smartroute_routes.csv",
                "text/csv",
                use_container_width=True,
            )
        with col_e2:
            json_data = json.dumps(summary, indent=2, default=str)
            st.download_button(
                "📥 Download Full JSON",
                json_data,
                "smartroute_results.json",
                "application/json",
                use_container_width=True,
            )

        st.subheader("API Request Body")
        st.caption("Use this JSON to call the `/optimize` API endpoint directly:")
        api_body = {
            "destinations": [{"lat": float(d[0]), "lon": float(d[1])} for d in destinations],
            "depots": [{"lat": float(d[0]), "lon": float(d[1])} for d in depots],
            "algorithm": summary["algorithm"],
        }
        st.json(api_body)


# ---------------------------------------------------------------------------
# Algorithm Comparison
# ---------------------------------------------------------------------------
if "comparison" in st.session_state:
    st.divider()
    st.subheader("📊 Algorithm Comparison")

    comparison = st.session_state["comparison"]
    comp_data = []
    for algo_name, res in comparison.items():
        fc_comp = res["fleet_cost"]
        comp_data.append({
            "Algorithm": ALGORITHMS.get(algo_name, algo_name),
            "Vehicles": fc_comp["total_vehicles"],
            "Distance (km)": fc_comp["total_distance_km"],
            "Cost ($)": fc_comp["total_fuel_cost_usd"],
            "CO₂ (kg)": fc_comp["total_co2_kg"],
            "Time (hrs)": fc_comp["total_time_hours"],
            "Opt Time (s)": res["optimization_time_seconds"],
        })

    comp_df = pd.DataFrame(comp_data)
    st.dataframe(comp_df, hide_index=True)

    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(
            comp_df,
            x="Algorithm",
            y="Distance (km)",
            title="Total Distance Comparison",
            color="Algorithm",
            color_discrete_sequence=px.colors.qualitative.Bold,
        )
        st.plotly_chart(fig)
    with c2:
        fig = px.bar(
            comp_df,
            x="Algorithm",
            y="Opt Time (s)",
            title="Optimization Speed",
            color="Algorithm",
            color_discrete_sequence=px.colors.qualitative.Pastel,
        )
        st.plotly_chart(fig)


# ---------------------------------------------------------------------------
# No results yet — show overview
# ---------------------------------------------------------------------------
if "result" not in st.session_state and "comparison" not in st.session_state:
    st.subheader("Preview: Data Points")

    m = folium.Map(
        location=[float(depots[:, 0].mean()), float(depots[:, 1].mean())],
        zoom_start=8,
        tiles="CartoDB positron",
    )
    for i, dest in enumerate(destinations):
        folium.CircleMarker(
            location=[float(dest[0]), float(dest[1])],
            radius=3,
            color="#667eea",
            fill=True,
            fill_opacity=0.4,
        ).add_to(m)
    for i, depot in enumerate(depots):
        folium.Marker(
            location=[float(depot[0]), float(depot[1])],
            tooltip=f"Depot {i}",
            icon=folium.Icon(color="red", icon="warehouse", prefix="fa"),
        ).add_to(m)

    st_folium(m, width=None, height=500)

    # How it works
    st.divider()
    st.subheader("How SmartRoute Pro Works")
    st.markdown("""
    **SmartRoute Pro** uses a 4-phase AI pipeline to optimize multi-depot vehicle routing:

    | Phase | Step | Method |
    |-------|------|--------|
    | 1 | **Depot Assignment** | Modified K-Means clustering assigns destinations to nearest depots |
    | 2 | **Vehicle Classification** | Near/far analysis determines vehicle types (pickup vs truck) |
    | 3 | **Vehicle Sub-clustering** | Capacity-aware K-Means splits stops into vehicle-sized groups |
    | 4 | **Route Optimization** | TSP solver (NN / 2-Opt / SA / GA) minimizes travel distance per vehicle |

    **Additional AI Features:**
    - 🤖 **ML Demand Forecasting** — Gradient Boosting predicts demand at each destination
    - 🌱 **CO₂ Tracking** — Real-time emissions estimation per vehicle and fleet-wide
    - 📊 **Algorithm Comparison** — Compare 4 optimization algorithms side by side
    - 🗺️ **Interactive Maps** — Folium-based visualization with route overlays
    """)
