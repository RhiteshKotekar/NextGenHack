# Insight-o-pedia Backend 🚀

AI-powered Flask backend for supply chain optimization chatbot.

## 🎯 Problem Statement

**Amazon India: Reimagining the AI-Driven Supply Chain Network**

This backend powers an intelligent chatbot that analyzes supply chain data to provide:
- 📈 Demand forecasting and seasonal predictions
- 📦 Inventory optimization and stock recommendations
- 🚚 Shipping delay analysis and courier performance
- 💬 Customer sentiment analysis from reviews
- 🏭 Warehouse efficiency optimization

---

## 🏗️ Architecture

```
backend/
├── app.py                 # Flask server with ML inference
├── train.py               # Model training scripts
├── utils.py              # Utility functions
├── requirements.txt      # Python dependencies
├── start.sh             # Quick start script
├── models/              # Trained ML models
│   ├── model_orders.pkl
│   ├── model_seasonal_prophet.pkl
│   ├── model_transport.pkl
│   ├── model_warehouse.pkl
│   └── sentiment_model.pkl
└── data/                # Training datasets
    ├── orders_sample.csv
    ├── seasonal_demand.csv
    ├── transportations_sample.csv
    ├── warehouse_ops_sample.csv
    └── customer_reviews_sample.csv
```

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Train Models (First Time Only)

```bash
# Train all models with sample data (5000 rows each)
python train.py orders 5000
python train.py seasonal 5000
python train.py warehouse 5000
python train.py transport 5000
python train.py reviews 5000

# Or train with full dataset (omit row limit)
python train.py orders
python train.py seasonal
```

### 3. Start Flask Server

```bash
# Option 1: Use start script (recommended)
./start.sh

# Option 2: Direct Python
python app.py
```

Server will run on: **http://localhost:5000**

---

## 📡 API Endpoints

### 1. **POST /chat** - Main Chatbot Endpoint

Send natural language questions and get AI-powered insights.

**Request:**
```json
{
  "question": "What will Q4 demand look like?"
}
```

**Response:**
```json
{
  "question": "What will Q4 demand look like?",
  "intent": "forecast",
  "params": {
    "quarter": "Q4",
    "months": [10, 11, 12]
  },
  "insights": [
    {
      "type": "forecast",
      "text": "📈 **Demand Forecast (Next 90 Days)**\n\n• Average demand index: 45.23\n• Trend: Increasing (12.5 points)\n• Peak demand expected: 67.8",
      "data": {
        "avg_demand": 45.23,
        "trend": 12.5,
        "forecast": [...]
      }
    }
  ],
  "timestamp": "2025-11-15T10:30:00"
}
```

### 2. **GET /health** - Health Check

Check server and model status.

**Response:**
```json
{
  "status": "healthy",
  "models_loaded": ["model_orders.pkl", "model_seasonal_prophet.pkl"],
  "timestamp": "2025-11-15T10:30:00"
}
```

### 3. **GET /** - Service Info

Get API documentation.

---

## 💬 Example Questions

### Forecasting / Demand
```
✓ "What will Q4 demand look like based on current trends?"
✓ "Predict the order value for the next 90 days."
✓ "Is there a seasonal increase expected in December?"
✓ "What's the demand forecast for the next quarter?"
```

### Inventory / Stock
```
✓ "If demand increases by 20%, what stock adjustments are needed?"
✓ "Which categories need stock boosting for Q4?"
✓ "Are we at risk of stockouts during peak season?"
✓ "Is our inventory level sufficient for predicted demand?"
```

### Shipping / Transport
```
✓ "How will shipping delays impact next quarter?"
✓ "Which courier partners might cause late deliveries?"
✓ "What are the top performing couriers?"
```

### Sentiment
```
✓ "How are customer reviews trending?"
✓ "Is customer sentiment positive this month?"
✓ "What's the average customer rating?"
```

### Warehouse
```
✓ "Which warehouses are underperforming?"
✓ "How can we improve warehouse efficiency?"
✓ "What's the average processing time?"
```

---

## 🤖 How It Works

### 1. **Intent Detection**
The system analyzes keywords to determine what the user is asking about:
- `forecast` → Demand predictions, seasonal trends
- `inventory` → Stock recommendations
- `shipping` → Courier performance, delays
- `sentiment` → Customer review analysis
- `warehouse` → Efficiency optimization

### 2. **Parameter Extraction**
Extracts key parameters from questions:
- Percentages: "20%" → `surge_pct: 0.2`
- Time periods: "Q4" → `months: [10, 11, 12]`
- Days: "90 days" → `days: 90`
- Months: "December" → `target_month: 12`

### 3. **Model Inference**
Routes to appropriate ML models:
- **Orders Model** (LightGBM): Predicts order values by category
- **Seasonal Model** (Prophet/LGBM): Forecasts demand trends
- **Transport Model**: Analyzes courier performance
- **Warehouse Model**: Evaluates processing efficiency
- **Sentiment Model** (VADER): Analyzes customer reviews

### 4. **Response Generation**
Formats insights with:
- ✅ Clear, actionable recommendations
- 📊 Data-driven metrics
- 💡 Strategic suggestions
- ⚠️ Risk assessments

---

## 🧪 Testing

### Test with curl:
```bash
# Forecast question
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What will Q4 demand look like?"}'

# Inventory question
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "If demand increases by 20%, what stock adjustments needed?"}'

# Health check
curl http://localhost:5000/health
```

### Test with Python:
```python
import requests

response = requests.post(
    'http://localhost:5000/chat',
    json={'question': 'What will Q4 demand look like?'}
)
print(response.json())
```

---

## 🔧 Configuration

### Environment Variables
- `FLASK_ENV`: Set to `development` for debug mode
- `FLASK_PORT`: Change server port (default: 5000)

### Model Customization
Edit `app.py` to:
- Add new intent types
- Customize response formatting
- Integrate additional ML models

---

## 📊 Data Sources

The system is trained on 5 datasets:

1. **orders_sample.csv** - Order transactions (date, city, warehouse, category, value)
2. **seasonal_demand.csv** - Historical demand with seasonal patterns
3. **transportations_sample.csv** - Courier performance, delivery times, fuel costs
4. **warehouse_ops_sample.csv** - Processing times, operational costs, workforce
5. **customer_reviews_sample.csv** - Customer feedback and ratings

---

## 🐛 Troubleshooting

### Models not found?
```bash
# Train models first
python train.py orders 5000
python train.py seasonal 5000
```

### Import errors?
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

### CORS errors from frontend?
```bash
# Make sure flask-cors is installed
pip install flask-cors
```

### Port already in use?
```bash
# Change port in app.py or:
kill -9 $(lsof -ti:5000)  # Kill process on port 5000
```

---

## 📈 Performance Metrics

- **Response Time**: ~200-500ms per query
- **Model Accuracy**: 
  - Orders RMSE: ~150 INR
  - Seasonal MAE: ~5 demand points
  - Sentiment Accuracy: ~85%

---

## 🚀 Deployment

### Docker (Optional)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

### Production Tips
- Use **gunicorn** instead of Flask dev server
- Enable **Redis** for model caching
- Add **rate limiting** for API protection
- Implement **authentication** for security

---

## 🤝 Integration with Frontend

The frontend (`chatbot-page.tsx`) calls this backend via:

```typescript
import { askModel } from "@/app/api/askModel";

const response = await askModel("What will Q4 demand look like?");
// Returns insights array with formatted responses
```

Make sure to:
1. Start backend on port 5000
2. Set `NEXT_PUBLIC_BACKEND_URL=http://localhost:5000` in frontend `.env.local`
3. Enable CORS in Flask (already configured)

---

## 📝 License

MIT License - Built for NextGenHackathon 2025

---

## 👥 Team

NextGenHackathon - Insight-o-pedia Team

**Project**: AI-Driven Supply Chain Optimization for Amazon India

---

🎉 **Ready to optimize your supply chain!**
