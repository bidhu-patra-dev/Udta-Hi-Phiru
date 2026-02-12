import pandas as pd
import os
CITY_DATA_PATH = "data/india_tourism_cities_with_lat_lon.csv"
TRANSPORT_COST_PER_KM = {
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


    try:
        from transformers import pipeline
        generator = pipeline(
            "text2text-generation",
            model="google/flan-t5-base"
        )
    except Exception:
        # If transformers or model aren't available in the environment,
        # fall back to a lightweight generator set to None. The
        # `generate_travel_plan` function below will handle this case
        # and return a simple, deterministic plan so the app doesn't error.
        generator = None


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

        # If a transformers pipeline is available, use it. Otherwise return
        # a simple deterministic plan so the Streamlit app can run without
        # heavy ML dependencies or internet access.
        if generator is not None:
            try:
                response = generator(
                    prompt,
                    max_length=256
                )
                return response[0].get("generated_text", str(response))
            except Exception:
                # Fall through to lightweight plan on any generation error
                pass

        # Lightweight fallback plan
        travel_info = None
        try:
            travel_info = estimate_travel(source_city, destination_city, transport_mode)
        except Exception:
            travel_info = {"distance": 0, "travel_cost": 0}

        stay_info = None
        try:
            stay_info = estimate_stay_and_food(destination_city, days)
        except Exception:
            stay_info = {"stay_cost": 0, "food_cost": 0}

        total_est = travel_info.get('travel_cost', 0) + stay_info.get('stay_cost', 0) + stay_info.get('food_cost', 0)

        plan_lines = []
        plan_lines.append(f"Best option: {transport_mode} — ₹{travel_info.get('travel_cost', 0)}")
        plan_lines.append(f"Estimated total cost: ₹{total_est}")
        plan_lines.append("Day-wise plan:")
        for d in range(1, max(1, days) + 1):
            plan_lines.append(f"{d}. Explore {destination_city} — highlights and local eats.")
        plan_lines.append("Budget hacks: choose off-peak travel, eat local, book shared stays.")

        return "\n".join(plan_lines)


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
