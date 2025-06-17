# backend/app.py (Updated for Random Forest ML Model)

from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
import datetime
import random
import joblib # Import joblib to load the model and encoders
import os # To check if model files exist

app = Flask(__name__)
CORS(app) # Enable CORS for frontend to communicate with backend

# --- ML Model Loading ---
ml_pipeline = None # Now loading the entire pipeline
unit_map = None

MODEL_DIR = 'models'
MODEL_PATH = os.path.join(MODEL_DIR, 'crop_price_rf_pipeline.pkl')
UNIT_MAP_PATH = os.path.join(MODEL_DIR, 'unit_map.pkl')

def load_ml_assets():
    global ml_pipeline, unit_map
    try:
        ml_pipeline = joblib.load(MODEL_PATH)
        unit_map = joblib.load(UNIT_MAP_PATH)
        print("ML pipeline and unit map loaded successfully!")
    except FileNotFoundError:
        print(f"ERROR: ML model pipeline or unit map files not found in '{MODEL_DIR}/'.")
        print("Please ensure you have run 'python train_model.py' in the 'backend' directory.")
        ml_pipeline = None # Set to None to trigger fallback
        unit_map = {} # Initialize empty map for safe access
    except Exception as e:
        print(f"Error loading ML assets: {e}")
        ml_pipeline = None
        unit_map = {}

# Load assets when the app starts
with app.app_context():
    load_ml_assets()

# --- Mock Data for Dropdowns (MUST BE CONSISTENT with train_model.py's MASTER_ lists) ---
# These are used to populate the dropdowns in the frontend.
MOCK_DATA = {
    "crop_categories": ["Cereals", "Vegetables", "Fruits", "Pulses", "Spices"],
    "crop_types_by_category": {
        "Cereals": ["Rice", "Wheat", "Maize", "Barley", "Oats"],
        "Vegetables": ["Tomato", "Potato", "Onion", "Spinach", "Carrot", "Cabbage"],
        "Fruits": ["Apple", "Banana", "Grapes", "Mango", "Orange", "Pomegranate"],
        "Pulses": ["Lentil", "Chickpea", "Mung Bean", "Pigeon Pea", "Black Gram"],
        "Spices": ["Turmeric", "Cumin", "Cardamom", "Black Pepper", "Cinnamon"]
    },
    "countries": ["India", "USA", "China", "Brazil", "Australia", "Canada"],
    "states_by_country": {
        "India": ["Karnataka", "Maharashtra", "Uttar Pradesh", "Punjab", "Gujarat", "Tamil Nadu", "Rajasthan", "Madhya Pradesh"],
        "USA": ["California", "Texas", "Florida", "Iowa", "Kansas", "Idaho", "Washington", "New York"],
        "China": ["Henan", "Shandong", "Sichuan", "Heilongjiang", "Hunan"],
        "Brazil": ["Mato Grosso", "Parana", "Minas Gerais", "Rio Grande do Sul", "Sao Paulo"],
        "Australia": ["New South Wales", "Victoria", "Queensland", "Western Australia", "South Australia"],
        "Canada": ["Ontario", "Saskatchewan", "Alberta", "Manitoba"]
    },
    "seasons": ["Kharif (Monsoon)", "Rabi (Winter)", "Zaid (Summer)", "Spring", "Autumn", "Winter"],
}


# --- ML Prediction Function (Uses the Loaded Random Forest Pipeline) ---
def get_ml_prediction(crop_type, season, country, state):
    if ml_pipeline is None:
        print("ML pipeline not loaded. Falling back to simple simulation.")
        return simulate_price_data_fallback(crop_type) # Fallback to original simulation

    try:
        # --- Prepare Input Features for Prediction ---
        # Get current date details
        current_date = datetime.date.today()
        current_year = current_date.year
        current_month = current_date.month

        # Simulate other dynamic features for the current prediction
        # In a real system, these would come from live data sources or more complex forecasting
        # We try to make them somewhat realistic or at least plausible for a demo
        simulated_rainfall = 70 + 60 * np.sin(np.pi * current_month / 6) + np.random.normal(0, 15)
        simulated_rainfall = max(0, simulated_rainfall)

        simulated_area_under_cultivation = 1000 + np.random.normal(0, 100) # Simple fixed + noise
        simulated_area_under_cultivation = max(100, simulated_area_under_cultivation)

        # For previous_year_price, a simple heuristic (e.g., base it off a recent historical average)
        # In a real model, this would be an actual historical price from your database
        simulated_previous_year_price = 5000 if "quintal" in unit_map.get(crop_type, "") else 80
        simulated_previous_year_price *= (1 + np.random.uniform(-0.1, 0.1)) # Add some variability

        # Create a DataFrame with the exact column names the pipeline was trained on
        # The order and names of columns MUST match the training data
        input_df = pd.DataFrame([[
            current_year, current_month, crop_type, season, country, state,
            simulated_rainfall, simulated_area_under_cultivation, simulated_previous_year_price
        ]], columns=[
            'year', 'month', 'crop_type', 'season', 'country', 'state',
            'rainfall', 'area_under_cultivation', 'previous_year_price'
        ])

        # Predict the price using the loaded pipeline
        predicted_price_value = ml_pipeline.predict(input_df)[0]
        predicted_price_value = max(1.0, predicted_price_value) # Ensure positive price

        # --- Simulate Historical and Future Data (for graph visualization) ---
        # This part is still simulated, but now it's centered around the ML prediction
        unit = unit_map.get(crop_type, "/unit")
        num_historical_months = 24
        num_future_months = 12

        # Simulate historical prices, ending near the predicted price
        # Make the 'current_price' reflect the most recent data point
        current_price = predicted_price_value * (1 + random.uniform(-0.05, 0.05)) # Close to prediction
        historical_prices = [current_price]
        for _ in range(num_historical_months - 1):
            # Simple reverse random walk
            historical_prices.append(max(10, historical_prices[-1] * (1 + random.uniform(-0.02, 0.02))))
        historical_prices.reverse() # Oldest to newest

        # Simulate future prices with a slight trend/seasonality from the prediction
        future_prices = []
        for i in range(num_future_months):
            # A bit more sophisticated seasonality around the predicted price
            seasonal_factor = 1 + 0.05 * np.sin(np.pi * (current_month + i) / 6) # Sine wave for seasonality
            trend_factor = 1 + 0.002 * i # Slight upward trend over future months
            future_price_sim = predicted_price_value * seasonal_factor * trend_factor + np.random.normal(0, predicted_price_value * 0.01)
            future_prices.append(max(10, future_price_sim))

        # Mock confidence scores (higher for near future, lower for far future)
        confidence_scores = [max(50, 95 - i*3 - random.uniform(0,5)) for i in range(num_future_months)]
        confidence_scores = [min(100, score) for score in confidence_scores]

        # Mock factors and recommendations based on simple heuristics or predefined text
        # In a real system, these would come from model interpretability or expert rules
        factors = {
            "weather": {
                "condition": f"Normal monsoon expected, with {simulated_rainfall:.0f}mm rainfall forecast. Localized showers likely.",
                "impact": "Generally favorable conditions for crop growth. Watch for potential excess rainfall.",
                "impact_color": "text-green-600" if simulated_rainfall > 50 else "text-yellow-600"
            },
            "supply": {
                "condition": f"Area under cultivation is {simulated_area_under_cultivation:.0f} hectares. Good harvest expected.",
                "impact": "Adequate supply anticipated, which may keep prices stable.",
                "impact_color": "text-yellow-600"
            },
            "demand": {
                "condition": "Domestic demand is steady, with moderate export interest.",
                "impact": "Consistent demand provides a floor for prices. No significant spikes expected.",
                "impact_color": "text-green-600"
            }
        }

        recommendations = {
            "sell_time": "The model suggests a moderate upward trend in the next 2-3 months. Consider selling during peak seasonal demand.",
            "trend_analysis": "Predicted trend shows slight seasonality with overall stability. Long-term (6-12 months) prices are expected to remain within a narrow range.",
            "alerts_enabled": True
        }

        return {
            "current_price": current_price,
            "predicted_price": predicted_price_value,
            "unit": unit,
            "historical_prices": historical_prices,
            "future_prices": future_prices,
            "confidence_scores": confidence_scores,
            "factors": factors,
            "recommendations": recommendations
        }

    except Exception as e:
        print(f"Error during ML prediction: {e}")
        return simulate_price_data_fallback(crop_type) # Fallback on any prediction error

# --- Fallback Simulation Function (Original one, slightly renamed) ---
def simulate_price_data_fallback(crop_type, num_historical_months=24, num_future_months=12):
    """
    Simulates historical and future price data for a given crop type.
    This is the fallback simulation if the ML model is not available or errors out.
    """
    seed = sum(ord(c) for c in crop_type)
    random.seed(seed)
    np.random.seed(seed)

    base_price = 0
    unit = unit_map.get(crop_type, "/unit") if unit_map else "/unit" # Use loaded map if available

    if unit == "/kg":
        base_price = random.uniform(20, 150)
        fluctuation_factor = 0.08
    elif unit == "/dozen":
        base_price = random.uniform(30, 100)
        fluctuation_factor = 0.07
    elif unit == "/quintal":
        base_price = random.uniform(1500, 8000)
        fluctuation_factor = 0.05
    else:
        base_price = random.uniform(10, 100)
        fluctuation_factor = 0.10

    historical_prices = []
    current_price_sim = base_price * (1 + random.uniform(-0.15, 0.15))
    for _ in range(num_historical_months):
        current_price_sim *= (1 + random.uniform(-fluctuation_factor, fluctuation_factor))
        historical_prices.append(max(10, current_price_sim))
    historical_prices.reverse()

    future_prices = []
    current_future_price_sim = historical_prices[-1] if historical_prices else base_price
    for i in range(num_future_months):
        seasonal_adjust = 1 + np.sin(i / 3.0 * np.pi) * 0.05
        trend_factor = 1 + random.uniform(-0.005, 0.01)
        current_future_price_sim *= (trend_factor * seasonal_adjust * (1 + random.uniform(-fluctuation_factor / 2, fluctuation_factor / 2)))
        future_prices.append(max(10, current_future_price_sim))

    predicted_avg_price = np.mean(future_prices[:3]) if future_prices else base_price
    confidence_scores = [max(50, 95 - i*3 - random.uniform(0,5)) for i in range(num_future_months)]
    confidence_scores = [min(100, score) for score in confidence_scores]

    factors = {
        "weather": {"condition": "Expected normal monsoon; potential for localized heavy rains in few regions.", "impact": "Overall positive outlook, but watch for regional disruptions.", "impact_color": "text-green-600"},
        "supply": {"condition": "Recent harvest was good, leading to moderate supply levels.", "impact": "Prices are currently stable due to sufficient supply.", "impact_color": "text-yellow-600"},
        "demand": {"condition": "Domestic demand is steady, with moderate export interest.", "impact": "Consistent demand provides a floor for prices.", "impact_color": "text-green-600"}
    }

    recommendations = {
        "sell_time": "The model suggests that the best time to sell could be in the next 2-3 months, as prices show a slight upward trend before seasonal increases in supply.",
        "trend_analysis": "The predicted trend indicates a gradual increase in price for the next quarter, followed by a plateau. Long-term outlook (6-12 months) suggests stability.",
        "alerts_enabled": True
    }

    return {
        "current_price": historical_prices[-1] if historical_prices else predicted_avg_price,
        "predicted_price": predicted_avg_price,
        "unit": unit,
        "historical_prices": historical_prices,
        "future_prices": future_prices,
        "confidence_scores": confidence_scores,
        "factors": factors,
        "recommendations": recommendations
    }


# --- API Endpoints ---

@app.route('/api/metadata', methods=['GET'])
def get_metadata():
    """
    Endpoint to provide initial data for dropdowns.
    Uses the expanded MOCK_DATA to reflect the broader synthetic dataset.
    """
    metadata_response = {
        "crop_categories": MOCK_DATA["crop_categories"],
        "crop_types_by_category": MOCK_DATA["crop_types_by_category"],
        "countries": MOCK_DATA["countries"],
        "states_by_country": MOCK_DATA["states_by_country"],
        "seasons": MOCK_DATA["seasons"]
    }
    return jsonify(metadata_response)

@app.route('/api/predict', methods=['POST'])
def predict_crop_price():
    """
    Endpoint to receive crop prediction request and return results.
    This now uses the loaded Random Forest ML pipeline for the core prediction.
    """
    data = request.get_json()

    crop_type = data.get('crop_type')
    season = data.get('season')
    country = data.get('country')
    state = data.get('state')

    # Validate that crucial parameters for the ML model are present
    if not all([crop_type, season, country, state]):
        return jsonify({"error": "Missing one or more required prediction parameters (crop type, season, country, state)."}), 400

    # Call the ML prediction function
    prediction_results = get_ml_prediction(crop_type, season, country, state)

    # Add back the input information for frontend display
    prediction_results["crop_type"] = crop_type
    prediction_results["season"] = season
    prediction_results["country"] = country
    prediction_results["state"] = state

    return jsonify(prediction_results)

# --- Run the Flask Application ---
if __name__ == '__main__':
    app.run(debug=True, port=5000)