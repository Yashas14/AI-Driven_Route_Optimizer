

# 🚀 SmartRoute Pro

### 🧠 AI-Powered Multi-Depot Route Optimization Engine

> Transforming logistics with AI, optimization algorithms, and real-time analytics.

---

## 🌍 Overview

**SmartRoute Pro** is a **production-grade AI system** that solves complex logistics challenges using advanced optimization and machine learning.

It tackles the **Multi-Depot Vehicle Routing Problem (MDVRP)** — one of the hardest real-world problems in supply chain and transportation.

💡 In simple terms:

> It finds the **most efficient routes** for multiple vehicles across multiple depots — saving **cost, time, and fuel**, while reducing **carbon emissions**.

---

## 🔥 Why This Project Stands Out

✨ Unlike basic routing projects, this system combines:

* 🧠 **Machine Learning + Optimization**
* ⚙️ **Multiple TSP Algorithms (4 implementations)**
* 📊 **Interactive Dashboard + API**
* 🌱 **CO₂ Emission Tracking**
* 🚚 **Multi-depot + multi-vehicle intelligence**

---

## 👨‍💻 Team

| Name                  | Contribution                                     |
| --------------------- | ------------------------------------------------ |
| **Yashas D**          | VRP Engine, Optimization Algorithms, Backend API |
| **M Shivani Kashyap** | Dashboard, ML Pipeline, Data Processing          |

🏆 Team: **TechTriad**

---

## 🧠 Core Intelligence

### 🔹 Optimization Algorithms

* Nearest Neighbor (⚡ fastest)
* 2-Opt (🔧 refinement)
* Simulated Annealing (🔥 escape local optima)
* Genetic Algorithm (🧬 best global solution)

---

### 🔹 Machine Learning Layer

* 📈 Demand Forecasting using Gradient Boosting
* 📍 Geo-based feature engineering
* 🔥 Smart clustering with KMeans

---

### 🔹 Smart Routing Pipeline

```text
Input Data → Clustering → Vehicle Allocation → Route Optimization → Analytics Output
```

---

## ⚙️ System Architecture

```text
SmartRoute Pro
│
├── 🚀 FastAPI Backend (REST APIs)
├── 📊 Streamlit Dashboard (Visualization)
├── 🧠 Core Engine
│   ├── TSP Algorithms
│   ├── VRP Engine
│   ├── Clustering Module
│   ├── Cost & Emission Estimator
│   └── Demand Forecasting Model
│
├── 🌍 Services
│   ├── Geocoding (OpenStreetMap)
│   └── Data Loader
│
└── 🧪 Testing Suite (pytest)
```

---

## 🚀 Key Features

### 🛣️ Intelligent Routing

* Multi-depot optimization
* Multi-vehicle allocation
* Distance + cost minimization

### 📊 Analytics Dashboard

* Interactive maps (Folium)
* Performance charts (Plotly)
* Demand heatmaps

### 🌱 Sustainability Tracking

* Fuel consumption estimation
* CO₂ emissions monitoring

### ⚡ Algorithm Benchmarking

* Compare all algorithms in real-time
* Choose best trade-off between speed & accuracy

---

## 🧪 API Capabilities

| Endpoint    | Purpose                       |
| ----------- | ----------------------------- |
| `/optimize` | Run route optimization        |
| `/compare`  | Compare algorithms            |
| `/geocode`  | Convert address → coordinates |
| `/demo`     | Sample dataset                |
| `/health`   | API status                    |

---

## 🧭 How It Works

### 4-Step Optimization Pipeline

1️⃣ **Depot Assignment**
→ Assign destinations to nearest depot using clustering

2️⃣ **Distance Classification**
→ Decide vehicle type (truck vs pickup)

3️⃣ **Vehicle Clustering**
→ Split deliveries based on capacity

4️⃣ **Route Optimization**
→ Apply TSP algorithm for best path

---

## ⚡ Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run Dashboard
python run.py dashboard

# Run API
python run.py api

# Run both
python run.py both
```

---

## 🐳 Docker Support

```bash
docker compose up --build
```

---

## 📊 Dashboard Highlights

* 🗺️ Live route visualization
* 📁 CSV upload support
* 📈 Fleet analytics
* 🔍 Algorithm comparison
* 📥 Export results (CSV/JSON)

---

## 🧱 Tech Stack

| Layer        | Technologies              |
| ------------ | ------------------------- |
| Backend      | FastAPI, Python           |
| ML/AI        | scikit-learn              |
| Optimization | Custom TSP algorithms     |
| Frontend     | Streamlit, Plotly, Folium |
| Data         | CSV, Geo-coordinates      |
| Deployment   | Docker                    |

---

## 📂 Project Structure

```text
app/
dashboard/
data/
tests/
run.py
Dockerfile
```

---

## 🧪 Testing

```bash
pytest tests/ -v
```

---

## 🌟 Real-World Applications

* 🚚 Logistics & Delivery Optimization
* 🏭 Supply Chain Management
* 🛒 E-commerce Routing
* 🌍 Smart City Planning
* 🚛 Fleet Management Systems

---

## 📈 Future Enhancements

* 🔴 Real-time traffic integration
* 📱 Mobile dashboard
* 🤖 Reinforcement Learning optimization
* ☁️ Cloud deployment (AWS/GCP)

---

## 📜 License

MIT License © 2025
**Yashas D & M Shivani Kashyap**

---

## ⭐ Final Note

> This project is not just an implementation —
> it's a **complete AI-powered logistics system** combining
> **optimization, machine learning, and real-world impact**.

---
