import pandas as pd
import os
CITY_DATA_PATH = "data/india_tourism_cities_with_lat_lon.csv"
TRANSPORT_COST_PER_KM = {
    "Bus": 1.5,        # ₹ per km
    "Train": 1.2,
    "Flight": 4.5,
    "Car": 3.0
}
def load_cities():
    df = pd.read_csv(CITY_DATA_PATH)
    return sorted(df["city"].tolist())

import math

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return int(2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a)))

def estimate_travel(source, destination, transport_mode):
    df = pd.read_csv(CITY_DATA_PATH)

    src = df[df['city'] == source].iloc[0]
    dst = df[df['city'] == destination].iloc[0]

    distance = haversine(src.lat, src.lon, dst.lat, dst.lon)

    cost_per_km = TRANSPORT_COST_PER_KM.get(transport_mode, 1.5)
    travel_cost = int(distance * cost_per_km)

    return {
        'distance': distance,
        'mode': transport_mode,
        'travel_cost': travel_cost
    }
from transformers import pipeline
generator = pipeline(
    "text2text-generation",
    model="google/flan-t5-base"
)

import random
import re

def generate_travel_plan(source_city, destination_city, budget, days, interest, transport_mode):
    prompt = f"""
Create a clean, student-friendly travel plan.

Start city: {source_city}
Destination city: {destination_city}
Preferred transport mode: {transport_mode}
Budget: ₹{budget}
Duration: {days} days
Interest: {interest}

Output rules:
- Do NOT repeat lines
- Do NOT show instructions
- Keep it concise
- Friendly tone

Format:
1. Best travel option & cost
2. Day-wise plan
3. Budget hacks
"""

    response = generator(
        prompt,
        max_length=256
    )

    return response[0]["generated_text"]
def estimate_stay_and_food(destination_city, days):
    df = pd.read_csv(CITY_DATA_PATH)
    city_row = df[df["city"] == destination_city].iloc[0]

    city_type = city_row["type"]

    stay_cost_map = {
        "Hill": 800,
        "Heritage": 800,
        "Beach": 1000,
        "Urban": 1000,
        "Spiritual": 600,
        "Adventure": 900,
        "Backwaters": 900,
        "Cultural": 800,
        "Desert": 700
    }

    stay_per_night = stay_cost_map.get(city_type, 800)
    total_stay_cost = stay_per_night * (days - 1 if days > 1 else 1)

    food_per_day = 300
    total_food_cost = food_per_day * days

    return {
        "city_type": city_type,
        "stay_cost": total_stay_cost,
        "food_cost": total_food_cost
    }
def estimate_total_cost(source, destination, days, transport_mode):
    travel = estimate_travel(source, destination, transport_mode)
    stay_food = estimate_stay_and_food(destination, days)

    total = (
        travel['travel_cost']
        + stay_food['stay_cost']
        + stay_food['food_cost']
    )

    return {
        'distance': travel['distance'],
        'mode': travel['mode'],
        'travel_cost': travel['travel_cost'],
        'stay_cost': stay_food['stay_cost'],
        'food_cost': stay_food['food_cost'],
        'city_type': stay_food['city_type'],
        'total_cost': total
    }