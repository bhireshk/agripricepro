AgriPricePro: AI-Powered Crop Price Prediction
🚀 Project Overview
AgriPricePro is a comprehensive full-stack web application demonstrating the development and integration of a machine learning-driven solution for agricultural commodity price forecasting. Built with a clear separation of concerns, it showcases robust backend logic, data processing pipelines, and an intuitive user interface, designed to provide actionable insights for farmers, traders, and agricultural stakeholders. This project highlights proficiency in modern web development, data science, and MLOps principles.

✨ Key Features & Technical Highlights
Full-Stack Development: Engineered a cohesive application with distinct frontend and backend architectures, demonstrating expertise in end-to-end web solution delivery.

Machine Learning Integration: Implemented a Random Forest Regressor trained on a real-world-like agricultural dataset to predict Average Price (INR/Quintal). This showcases practical application of supervised learning for regression tasks.

Data Handling & Preprocessing: Demonstrated skills in loading, cleaning, and transforming structured data using Pandas, including handling missing values, categorical encoding (OneHotEncoder), and numerical scaling (StandardScaler).

ML Pipeline Management: Utilized sklearn.pipeline.Pipeline and joblib for efficient model training, serialization, and deserialization, ensuring seamless integration and deployment readiness.

RESTful API Design: Developed a Python Flask backend to expose well-defined API endpoints (/api/metadata, /api/predict) for seamless communication with the frontend.

Interactive User Interface: Crafted a responsive and intuitive web frontend using HTML, Tailwind CSS, and JavaScript, prioritizing user experience and data accessibility.

Data Visualization: Integrated Chart.js to dynamically render predicted future prices and simulated historical trends, enabling clear visual analysis of forecasts.

Insight Generation: Programmed logic to generate contextual "Key Factors Influencing Price" and "AI Recommendations," demonstrating an understanding of how to translate model outputs into business value.

Version Control & Modularity: Project structured for maintainability and scalability, ready for collaborative development and deployment via Git/GitHub.

🛠️ Technologies & Libraries
Frontend:

HTML5: Semantic structuring of web content.

Tailwind CSS: Streamlined CSS framework for rapid UI development and responsive design.

JavaScript (ES6+): Client-side interactivity, asynchronous operations (fetch API), and DOM manipulation.

Chart.js: Powerful library for creating interactive and customizable charts.

Font Awesome: Icon library for enhanced UI aesthetics.

Backend (Python 3.x):

Flask: Lightweight and flexible microframework for API development.

Flask-CORS: Manages Cross-Origin Resource Sharing for secure inter-service communication.

Pandas: Essential for efficient data loading, manipulation, and preparation.

NumPy: Core library for numerical computing, supporting array operations.

Scikit-learn: Comprehensive ML library for model training, preprocessing, and pipeline creation.

RandomForestRegressor, OneHotEncoder, StandardScaler, ColumnTransformer, Pipeline.

Joblib: Python library for saving and loading Python objects, crucial for ML model persistence.

📁 Project Structure
agripricepro-app/
├── frontend/
│   ├── index.html           # Main web page structure
│   ├── style.css            # Custom CSS styles
│   └── script.js            # Frontend JavaScript logic and API calls
│
└── backend/
    ├── app.py               # Flask API server, loads ML model and handles requests
    ├── requirements.txt     # Python dependencies for the backend
    ├── train_model.py       # Script to load dataset, preprocess, train ML model, and save assets
    ├── pricesofagriculture.xlsx # User-provided dataset file
    └── models/              # Directory for trained ML models and metadata
        ├── crop_price_rf_pipeline.pkl # Saved RandomForestRegressor model pipeline
        └── app_metadata.pkl         # Saved metadata (dropdown options, unit map, feature order)
    ├── venv/                # Python Virtual Environment (local development)
        └── (Contains project-specific Python interpreter and installed libraries)

🚀 Getting Started (Local Development)
Follow these steps to set up and run the AgriPricePro application on your local machine.

Prerequisites
Python 3.7+

pip (Python package installer)

Step 1: Clone the Repository
git clone <your-github-repo-url>
cd agripricepro-app

Step 2: Place Your Dataset
Ensure your Excel file, pricesofagriculture.xlsx, is located directly within the backend/ directory.

Important: The DATASET_PATH variable in backend/train_model.py is currently set to an absolute path (r'C:\Users\Bhiresh\Desktop\agripricepro\pricesofagriculture.xlsx'). For general GitHub usage, it is recommended to change this to a relative path if the file will always be in the backend/ folder:

DATASET_PATH = 'pricesofagriculture.xlsx'

Please adjust this in train_model.py after cloning/downloading for portability.

Step 3: Backend Setup (Python Environment)
Navigate to the backend directory:

cd backend

Create and activate a Python virtual environment:
This isolates your project's dependencies, ensuring a clean environment.

python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
# source venv/bin/activate

Your terminal prompt will typically show (venv) at the beginning once activated.

Install backend dependencies:

pip install -r requirements.txt

This will install all necessary Python libraries (Flask, scikit-learn, pandas, numpy, Flask-CORS, etc.).

Train the ML model:
This script loads your dataset, performs preprocessing, trains the RandomForestRegressor pipeline, and saves the trained model (.pkl files) into the models/ directory. This step is crucial and must complete without errors.

python train_model.py

Step 4: Frontend Adjustments
Ensure your frontend/index.html includes <select> elements for District and Market within the prediction form. Your frontend/script.js should then be updated to:

Select these new dropdown elements by their IDs.

Add event listeners to populate District based on State selection, and Market based on District selection, utilizing the app_metadata object fetched from the backend.

Modify the predictBtn's click listener to send all relevant input parameters (crop_category, district, market, alongside existing ones) in the JSON payload to the backend's /api/predict endpoint.

▶️ Running the Application
Start the Backend Server:

Open your terminal/command prompt.

Navigate to the backend/ directory.

Ensure your virtual environment is activated.

Run:

python app.py

You should see output similar to * Running on http://127.0.0.1:5000. Keep this terminal window open.

Open the Frontend:

Navigate to the frontend/ directory in your file explorer.

Double-click index.html to open it in your preferred web browser.

The frontend will automatically establish communication with your running backend, populating dropdowns and enabling predictions.

🧠 Machine Learning Model Explained
The core of AgriPricePro's prediction capability lies in its Random Forest Regressor model. This ensemble learning algorithm operates on the principle of "wisdom of the crowd."

Training Phase (train_model.py): The model is trained on your provided historical pricesofagriculture.xlsx dataset. Instead of learning a single set of rules, the RandomForestRegressor constructs multiple independent Decision Trees. Each tree is trained on a random subset of your data rows and considers only a random subset of features (e.g., Crop Type, Season, Rainfall, Previous Year Price) at each decision point. This randomization ensures diversity among the individual trees.

Prediction Phase (app.py): When a user requests a prediction, the input features (both user-selected and dynamically simulated values for environmental factors and historical context) are fed to every single trained Decision Tree within the Random Forest. Each tree independently generates its own price prediction. The final Average Price (INR/Quintal) displayed in the frontend is the average of all these individual predictions. This averaging process significantly improves robustness and generalization performance compared to a single decision tree.

Feature Integration: The model leverages comprehensive features from your dataset, including categorical inputs (one-hot encoded) and numerical features (standardized), to capture complex, non-linear relationships impacting crop prices.

📈 Scalability & Future Vision
This project is built with scalability in mind and lays the groundwork for advanced capabilities:

Real-time Data Integration: Future iterations can connect to live external APIs for up-to-the-minute weather, market, and production data, moving beyond current feature simulation.

Advanced Time-Series Forecasting: Explore and implement specialized time-series models (e.g., Prophet, ARIMA, LSTM neural networks) to provide more accurate and nuanced multi-step future price projections.

Model Interpretability (XAI): Integrate techniques to explain model decisions (e.g., SHAP, LIME) to highlight the most influential factors for each specific prediction.

Persistent User Data: Incorporate a cloud-based database (e.g., Google Firestore, AWS DynamoDB) for user authentication, saving prediction history, and personalized alert management.

Enhanced UI/UX: Develop more interactive dashboards, maps, and streamlined user workflows for a richer experience.

Containerization & Cloud Deployment: Utilize Docker for containerization and deploy the application to cloud platforms (AWS, Google Cloud, Azure) for production-level availability and automated scaling.

📧 Contact
Your Name: Bhiresh Siddappa Kannur

Email:bhireshkannur@gmail.com
