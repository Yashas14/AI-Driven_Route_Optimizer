# SmartRoute Pro — AI-Driven Route Optimization Engine

**Developed by Yashas D and M Shivani Kashyap | Team: TechTriad**

Production-grade multi-depot vehicle routing optimizer with ML demand forecasting, multiple TSP algorithms, interactive visualization, and REST API.

## Authors

| Name | Role |
|------|------|
| **Yashas D** | Core algorithm development, VRP engine, backend API |
| **M Shivani Kashyap** | Dashboard, data pipeline, ML demand forecasting |

**Team:** TechTriad

## What It Does

SmartRoute Pro solves the **Multi-Depot Vehicle Routing Problem (MDVRP)** — given a set of warehouse depots and delivery destinations, it finds the optimal routes for a heterogeneous vehicle fleet to minimize total travel distance, fuel cost, and CO₂ emissions.

### Core AI/ML Features

| Feature | Technology | Description |
|---------|-----------|-------------|
| **4 TSP Algorithms** | Custom implementations | Nearest Neighbor, 2-Opt, Simulated Annealing, Genetic Algorithm |
| **Smart Clustering** | scikit-learn KMeans | Multi-phase depot assignment + vehicle sub-clustering |
| **Demand Forecasting** | Gradient Boosting | ML model predicts delivery demand from geographic features |
| **Cost & CO₂ Estimation** | Physics-based model | Per-vehicle fuel consumption and emissions tracking |
| **Algorithm Comparison** | Benchmarking engine | Compare all 4 algorithms side-by-side on same data |

### Architecture

```
SmartRoute Pro
├── FastAPI Backend ──── REST API with Pydantic validation
├── Streamlit Dashboard ── Interactive maps, charts, analytics
├── Core Engine
│   ├── TSP Solvers ──── NN, 2-Opt, SA, Genetic Algorithm
│   ├── VRP Engine ───── Multi-depot orchestration pipeline
│   ├── Clustering ───── KMeans/nearest depot assignment
│   ├── Cost Estimator ── Fuel, time, CO₂ calculations
│   └── Demand ML ────── Gradient Boosting forecaster
├── Services
│   ├── Geocoding ────── OpenStreetMap Nominatim (free)
│   └── Data Loader ──── CSV upload, export, sample data
└── Tests ────────────── pytest suite with 20+ test cases
```

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Dashboard
```bash
python run.py dashboard
# Opens at http://localhost:8501
```

### 3. Run the API Server
```bash
python run.py api
# Swagger docs at http://localhost:8000/docs
```

### 4. Run Both
```bash
python run.py both
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check with available algorithms |
| `GET` | `/algorithms` | List optimization algorithms |
| `GET` | `/demo` | Get demo data for testing |
| `POST` | `/optimize` | Run route optimization |
| `POST` | `/compare` | Compare multiple algorithms |
| `POST` | `/geocode` | Geocode address to coordinates |

### Example: Optimize Routes
```bash
curl -X POST http://localhost:8000/optimize \
  -H "Content-Type: application/json" \
  -d '{
    "destinations": [
      {"lat": 48.88, "lon": 2.35},
      {"lat": 49.05, "lon": 2.35},
      {"lat": 48.70, "lon": 2.10}
    ],
    "depots": [{"lat": 48.85, "lon": 2.35}],
    "algorithm": "genetic_algorithm"
  }'
```

## Optimization Pipeline

The engine uses a **4-phase optimization pipeline**:

1. **Depot Assignment** — Modified KMeans clustering assigns each destination to its nearest depot
2. **Distance Classification** — Near/far split determines vehicle types (pickup for nearby, truck for distant)
3. **Vehicle Sub-clustering** — Capacity-aware KMeans splits stops into vehicle-sized groups
4. **TSP Optimization** — Selected algorithm (NN/2-Opt/SA/GA) minimizes travel distance per vehicle

## TSP Algorithms Explained

| Algorithm | Complexity | Quality | Speed | Best For |
|-----------|-----------|---------|-------|----------|
| **Nearest Neighbor** | O(n²) | Baseline | Fastest | Quick estimates, large datasets |
| **2-Opt** | O(n²k) | Good | Fast | Improving existing routes |
| **Simulated Annealing** | O(iterations) | Very Good | Medium | Escaping local optima |
| **Genetic Algorithm** | O(pop × gen × n) | Best | Slower | Final production optimization |

## Dashboard Features

- **Interactive Folium Map** — Route visualization with depot/destination markers
- **Upload CSV** — Custom data with lat/lon columns
- **Fleet Analytics** — Distance, cost, emissions charts (Plotly)
- **Demand Heatmap** — ML-predicted demand visualization
- **Algorithm Comparison** — Side-by-side benchmarks
- **Export** — Download routes as CSV or JSON

## Docker

```bash
docker compose up --build
# API: http://localhost:8000
# Dashboard: http://localhost:8501
```

## Testing

```bash
pytest tests/ -v
```

## Tech Stack

- **Backend**: Python 3.11+, FastAPI, Pydantic
- **ML/AI**: scikit-learn (KMeans, Gradient Boosting), custom TSP implementations
- **Frontend**: Streamlit, Folium, Plotly
- **Geocoding**: OpenStreetMap Nominatim (free, no API key)
- **Deployment**: Docker, Docker Compose

## Project Structure

```
├── app/
│   ├── api.py                  # FastAPI REST endpoints
│   ├── config.py               # Configuration management
│   ├── core/
│   │   ├── tsp_solver.py       # 4 TSP algorithms
│   │   ├── vrp_engine.py       # VRP optimization orchestrator
│   │   ├── clustering.py       # Depot assignment & vehicle splitting
│   │   ├── cost_estimator.py   # Fuel, time, CO₂ estimation
│   │   └── demand_forecaster.py # ML demand prediction
│   ├── models/
│   │   └── schemas.py          # Pydantic request/response models
│   ├── services/
│   │   ├── geocoding.py        # Address geocoding
│   │   └── data_loader.py      # Data I/O and CSV parsing
│   └── utils/
│       └── geo.py              # Haversine, distance matrix utilities
├── dashboard/
│   └── app.py                  # Streamlit interactive dashboard
├── data/
│   ├── sample_sources.csv      # Demo depot data
│   └── sample_destinations.csv # Demo destination data
├── tests/
│   └── test_optimizer.py       # Test suite (20+ tests)
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── run.py                      # Entry point
└── README.md
```

## License

MIT License — Copyright (c) 2025 **Yashas D** and **M Shivani Kashyap**, Team TechTriad.
See [LICENSE](LICENSE) for full details.

