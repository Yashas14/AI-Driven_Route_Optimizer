
# 🌟 **AI-Driven Route Optimizer**

**Short Project Description:** AI-based route optimization and visualization tool for sales vehicles.
 _Optimization Mode_: Maximize the total Potential Sales Delivered with constraints in inputs in minimum cost
_Recommendation Mode_: Recommend the Location of Distribution Points and/or Number of Vehicles, Types of vehicles at the distribution Point to cover X% of Potential sales and best cost for that coverage.
_Visualization_: The tool is supported by a visualization in Streamlit and Mapbox which shows the delivery Points, distribution Points and the calculated route for each delivery vehicle.

## **Problem Statement:**  
Build a Route Optimization tool that uses AI to generate optimized routes for better traffic control and fuel efficiency in real-time.

## **Welcome to SmartRoute!**  
In the ever-evolving world of logistics and supply chain management, **SmartRoute** stands as a beacon of efficiency. Our AI-driven tool is designed to revolutionize the way sales vehicles navigate, optimizing routes to ensure maximum efficiency, reduced fuel consumption, and real-time traffic adaptability. 

## 🚀 **Project Overview**
SmartRoute is not just a tool; it's a game-changer. By integrating cutting-edge AI algorithms with dynamic visualization, SmartRoute ensures that every delivery is optimized for success.

- **Optimization Mode:** Our AI models crunch the numbers to deliver routes that maximize potential sales while keeping costs to a minimum. Think of it as your sales fleet’s personal navigator, always finding the best path forward.
- **Recommendation Mode:** Need strategic advice? SmartRoute provides recommendations on where to place distribution points, how many vehicles you need, and the best mix of vehicle types to hit your sales targets—all while staying cost-effective.
- **Visualization:** Powered by Streamlit and Mapbox, our tool offers an interactive visualization of routes, delivery points, and distribution centers. See the bigger picture and dive into the details with ease.

**Data used:** Synthetic data based on [The heterogeneous fleet vehicle routing problem with overloads and time windows]( https://www.sciencedirect.com/science/article/pii/S0925527313000388) after heavy modification according to the given specifications.

## 💡 **What Powers SmartRoute?**
Our project is built on a solid foundation of synthetic data, inspired by research on vehicle routing problems. We customized this data to fit the unique challenges we aimed to solve.

### **Tech Stack:**
- **Azure Maps:** The backbone of our routing capabilities.
- **Azure Machine Learning:** Training our custom k-NN model to perfection.
- **Azure Notebooks:** Where ideas are prototyped and data is dissected.
- **Azure App Service:** Seamless web deployment for our user-friendly interface.

## 🏆 **Hackathon Glory**
**SmartRoute** was our submission for **QuantumX24**, a prestigious hackathon organized by New Horizon College of Engineering, Bengaluru. Our team, **TechTriad**, pushed the boundaries of what's possible in real-time route optimization. We experimented with various approaches before perfecting our custom heuristic algorithm, making SmartRoute both powerful and efficient.

## 🔥 Hackathon Pitch

In the fast-developing logistics and supply chain management fields, one of the critical problems in the decision-making system is that how to arrange a proper supply chain for a lot of destinations and suppliers and produce a detailed supply schedule under a set of constraints. Solutions to the multisource vehicle routing problem (MDVRP) help in solving this problem in case of transportation applications.

Given the locations of sources and destinations, the MDVRP requires the assignment of destination to sources and the vehicle routing for visiting them. Each vehicle originates from one source, serves the destinations assigned to that source, and returns to the same source. The objective of the MDVRP is to serve all destinations while minimizing the total travel distance (hence cost) under the constraint that the total demands of served destinations cannot exceed the capacity of the vehicle for each route.

This project uses a heuristic algorithm to solve this problem. The proposed algorithm consists of two phases:

* Phase 1: Find the destination nodes which will be catered by each source node using a modified k-means clustering algorithm.
* Phase 2: Do preliminary analysis on the points for determining the type and number of the vehicles for given constraints.
* Phase 3: Assign the vehicle to the subsets of the destination points using K-means while minimizing the fuel cost.
* Phase 4: Optimize the routing for the allotted locations using _Travelling Salesman_ optimization) for each vehicle.

## 🔦 Other highlights

The hackathon was a great learning opportunity to get familiar with cloud-based development. Since we were free to choose our dataset, a considerable effort put into ensuring our synthetic data was sufficiently realistic. Apart from that, we experimented with multiple existing approaches to VRP, including genetic algorithms and recursive-DBSCAN. However, we found our strategy to be most performant when scaled industrial level. One of the primary reasons is the relative simplicity and the speed of execution, which allows much-needed flexibility. 





