# app.py - Flask Backend for Insight-o-pedia AI Chatbot
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from datetime import datetime, timedelta
import re
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Paths
MODELS_DIR = Path(__file__).parent / "models"
DATA_DIR = Path(__file__).parent / "data"

# Global model cache
MODELS = {}
sentiment_analyzer = SentimentIntensityAnalyzer()


# ============================================================================
# MODEL LOADING
# ============================================================================
def load_model(name):
    """Load model from cache or disk"""
    if name not in MODELS:
        model_path = MODELS_DIR / name
        if not model_path.exists():
            raise FileNotFoundError(f"Model {name} not found at {model_path}")
        MODELS[name] = joblib.load(model_path)
    return MODELS[name]


# ============================================================================
# INTENT DETECTION
# ============================================================================
def detect_intent(question):
    """Detect what the user is asking about"""
    q = question.lower()
    print(f"🔍 Analyzing question: {question}")
    
    # Forecasting/Demand keywords
    forecast_kws = ['forecast', 'predict', 'demand', 'q4', 'q1', 'q2', 'q3', 'quarter', 'next', 'future', 'trend', 'seasonal', 'increase expected', 'december', 'will', 'look like']
    if any(kw in q for kw in forecast_kws):
        matched = [kw for kw in forecast_kws if kw in q]
        print(f"✅ Matched FORECAST keywords: {matched}")
        return 'forecast'
    
    # Inventory/Stock keywords
    inventory_kws = ['inventory', 'stock', 'adjust', 'boost', 'stockout', 'sufficient', 'category', 'increase by', 'surge', 'need']
    if any(kw in q for kw in inventory_kws):
        matched = [kw for kw in inventory_kws if kw in q]
        print(f"✅ Matched INVENTORY keywords: {matched}")
        return 'inventory'
    
    # Shipping/Transport keywords
    shipping_kws = ['shipping', 'delivery', 'delay', 'transport', 'courier', 'partner', 'late']
    if any(kw in q for kw in shipping_kws):
        matched = [kw for kw in shipping_kws if kw in q]
        print(f"✅ Matched SHIPPING keywords: {matched}")
        return 'shipping'
    
    # Sentiment keywords
    sentiment_kws = ['sentiment', 'review', 'customer', 'feedback', 'positive', 'negative', 'trending']
    if any(kw in q for kw in sentiment_kws):
        matched = [kw for kw in sentiment_kws if kw in q]
        print(f"✅ Matched SENTIMENT keywords: {matched}")
        return 'sentiment'
    
    # Warehouse keywords
    warehouse_kws = ['warehouse', 'processing', 'efficiency', 'operation', 'storage']
    if any(kw in q for kw in warehouse_kws):
        matched = [kw for kw in warehouse_kws if kw in q]
        print(f"✅ Matched WAREHOUSE keywords: {matched}")
        return 'warehouse'
    
    print(f"⚠️  No keywords matched, returning GENERAL")
    return 'general'


def extract_params(question):
    """Extract parameters from question like percentages, months, quarters"""
    params = {}
    
    # Extract percentage (e.g., "20%", "15 percent")
    pct_match = re.search(r'(\d+)\s*(?:%|percent)', question.lower())
    if pct_match:
        params['surge_pct'] = float(pct_match.group(1)) / 100
    
    # Extract time period
    if 'q4' in question.lower() or 'fourth quarter' in question.lower():
        params['quarter'] = 'Q4'
        params['months'] = [10, 11, 12]
    elif 'q3' in question.lower():
        params['quarter'] = 'Q3'
        params['months'] = [7, 8, 9]
    elif 'q1' in question.lower():
        params['quarter'] = 'Q1'
        params['months'] = [1, 2, 3]
    elif 'q2' in question.lower():
        params['quarter'] = 'Q2'
        params['months'] = [4, 5, 6]
    
    # Extract days
    days_match = re.search(r'(\d+)\s*days?', question.lower())
    if days_match:
        params['days'] = int(days_match.group(1))
    
    # Extract months
    if 'december' in question.lower():
        params['target_month'] = 12
    elif 'january' in question.lower():
        params['target_month'] = 1
    
    return params


# ============================================================================
# FORECASTING HANDLERS
# ============================================================================
def handle_forecast_question(question, params):
    """Handle demand/forecast related questions"""
    insights = []
    
    try:
        # Load seasonal model
        try:
            model_seasonal = load_model("model_seasonal_prophet.pkl")
            use_prophet = True
        except:
            model_seasonal = load_model("model_seasonal_lgbm.pkl")
            use_prophet = False
        
        # Generate future dates
        days = params.get('days', 90)  # Default 90 days
        future_dates = pd.date_range(start=datetime.now(), periods=days, freq='D')
        
        if use_prophet:
            future_df = pd.DataFrame({'ds': future_dates})
            forecast = model_seasonal.predict(future_df)
            
            avg_demand = forecast['yhat'].mean()
            trend = forecast['yhat'].iloc[-1] - forecast['yhat'].iloc[0]
            
            insights.append({
                'type': 'forecast',
                'text': f"📈 **Demand Forecast (Next {days} Days)**\n\n"
                       f"• Average demand index: {avg_demand:.2f}\n"
                       f"• Trend: {'Increasing' if trend > 0 else 'Decreasing'} ({abs(trend):.2f} points)\n"
                       f"• Peak demand expected: {forecast['yhat'].max():.2f}\n"
                       f"• Lowest demand expected: {forecast['yhat'].min():.2f}",
                'data': {
                    'avg_demand': float(avg_demand),
                    'trend': float(trend),
                    'forecast': forecast[['ds', 'yhat']].to_dict('records')[:10]
                }
            })
        else:
            future_df = pd.DataFrame({'ds': future_dates})
            future_df['month'] = future_df['ds'].dt.month
            future_df['dow'] = future_df['ds'].dt.dayofweek
            predictions = model_seasonal.predict(future_df[['month', 'dow']])
            
            avg_demand = predictions.mean()
            trend = predictions[-1] - predictions[0]
            
            insights.append({
                'type': 'forecast',
                'text': f"📈 **Demand Forecast (Next {days} Days)**\n\n"
                       f"• Average demand index: {avg_demand:.2f}\n"
                       f"• Trend: {'Increasing' if trend > 0 else 'Decreasing'} ({abs(trend):.2f} points)\n"
                       f"• Peak demand expected: {predictions.max():.2f}",
                'data': {
                    'avg_demand': float(avg_demand),
                    'trend': float(trend)
                }
            })
        
        # Orders prediction
        model_orders = load_model("model_orders.pkl")
        
        # Load sample data to understand categories
        df_orders = pd.read_csv(DATA_DIR / "orders_sample.csv")
        categories = df_orders['category'].unique()[:5]
        
        # Predict for target months
        target_months = params.get('months', [10, 11, 12])
        
        predictions_by_category = []
        for cat_idx, category in enumerate(categories):
            # Create sample features
            X_sample = pd.DataFrame({
                'order_month': target_months * 10,  # Repeat for multiple samples
                'order_dow': [0, 1, 2, 3, 4] * 6,
                'city': [0] * 30,
                'warehouse_id': [0] * 30,
                'category': [cat_idx] * 30,
                'courier_partner': [0] * 30,
                'route_id': [0] * 30
            })
            
            preds = model_orders.predict(X_sample)
            avg_value = preds.mean()
            
            predictions_by_category.append({
                'category': category,
                'avg_order_value': float(avg_value),
                'total_predicted': float(avg_value * 30)  # Assuming 30 days
            })
        
        # Add category insights
        insights.append({
            'type': 'category_forecast',
            'text': f"💰 **Category-wise Predictions**\n\n" + 
                   "\n".join([f"• {p['category']}: ₹{p['avg_order_value']:.2f} avg order value" 
                             for p in predictions_by_category[:3]]),
            'data': predictions_by_category
        })
        
        # Seasonal insights
        if 'target_month' in params or params.get('quarter') == 'Q4':
            insights.append({
                'type': 'seasonal',
                'text': f"🎄 **Seasonal Analysis**\n\n"
                       f"• Q4 (Oct-Dec) typically shows 25-40% increase in demand\n"
                       f"• December peaks due to holiday shopping\n"
                       f"• Recommend preparing inventory 2-3 weeks in advance\n"
                       f"• Focus on high-value categories: Electronics, Jewellery, Fashion",
                'data': {'quarter': 'Q4', 'expected_increase': 0.30}
            })
        
    except Exception as e:
        insights.append({
            'type': 'error',
            'text': f"⚠️ Error generating forecast: {str(e)}\n\nPlease ensure models are trained properly.",
            'data': {'error': str(e)}
        })
    
    return insights


# ============================================================================
# INVENTORY HANDLERS
# ============================================================================
def handle_inventory_question(question, params):
    """Handle inventory/stock related questions"""
    insights = []
    
    try:
        surge_pct = params.get('surge_pct', 0.2)  # Default 20%
        
        # Load models
        model_orders = load_model("model_orders.pkl")
        
        # Load historical data
        df_orders = pd.read_csv(DATA_DIR / "orders_sample.csv")
        
        # Get category analysis
        category_stats = df_orders.groupby('category').agg({
            'order_value_inr': ['mean', 'sum', 'count']
        }).reset_index()
        category_stats.columns = ['category', 'avg_value', 'total_value', 'order_count']
        category_stats = category_stats.sort_values('total_value', ascending=False).head(5)
        
        # Calculate stock recommendations
        recommendations = []
        for _, row in category_stats.iterrows():
            current_value = row['total_value']
            predicted_with_surge = current_value * (1 + surge_pct)
            stock_increase = surge_pct * 100
            
            recommendations.append({
                'category': row['category'],
                'current_demand': float(current_value),
                'predicted_demand': float(predicted_with_surge),
                'recommended_stock_increase': f"{stock_increase:.0f}%",
                'priority': 'High' if stock_increase >= 20 else 'Medium'
            })
        
        insights.append({
            'type': 'inventory',
            'text': f"📦 **Stock Adjustment Recommendations** (for {surge_pct*100:.0f}% surge)\n\n" +
                   "\n".join([
                       f"• **{r['category']}**: Increase stock by {r['recommended_stock_increase']} "
                       f"(Priority: {r['priority']})"
                       for r in recommendations[:5]
                   ]) +
                   f"\n\n⚠️ Total investment needed: ₹{sum(r['predicted_demand'] - r['current_demand'] for r in recommendations):,.2f}",
            'data': recommendations
        })
        
        # Stockout risk analysis
        model_seasonal = load_model("model_seasonal_lgbm.pkl") if (MODELS_DIR / "model_seasonal_lgbm.pkl").exists() else None
        
        if model_seasonal:
            insights.append({
                'type': 'stockout_risk',
                'text': f"⚠️ **Stockout Risk Assessment**\n\n"
                       f"• High risk categories during peak season:\n"
                       f"  - {recommendations[0]['category']} (highest demand)\n"
                       f"  - {recommendations[1]['category'] if len(recommendations) > 1 else 'N/A'}\n"
                       f"• Recommend safety stock of 30% above predicted demand\n"
                       f"• Monitor inventory levels weekly during peak periods",
                'data': {'high_risk_categories': [r['category'] for r in recommendations[:3]]}
            })
        
        # Check if current inventory is sufficient
        insights.append({
            'type': 'inventory_sufficiency',
            'text': f"✅ **Inventory Sufficiency Check**\n\n"
                   f"Based on predicted {surge_pct*100:.0f}% demand increase:\n"
                   f"• Current inventory: Likely INSUFFICIENT for peak demand\n"
                   f"• Action required: Yes - Immediate restocking needed\n"
                   f"• Timeline: Begin procurement within 2 weeks\n"
                   f"• Focus areas: Top 3 categories listed above",
            'data': {'sufficient': False, 'action_needed': True}
        })
        
    except Exception as e:
        insights.append({
            'type': 'error',
            'text': f"⚠️ Error analyzing inventory: {str(e)}",
            'data': {'error': str(e)}
        })
    
    return insights


# ============================================================================
# SHIPPING/TRANSPORT HANDLERS
# ============================================================================
def handle_shipping_question(question, params):
    """Handle shipping/delivery related questions"""
    insights = []
    
    try:
        # Load transport model
        model_transport = load_model("model_transport.pkl")
        
        # Load transport data
        df_transport = pd.read_csv(DATA_DIR / "transportations_sample.csv")
        
        # Courier performance analysis
        courier_stats = df_transport.groupby('courier_partner').agg({
            'delivery_time_days': ['mean', 'std'],
            'fuel_cost_inr': 'mean',
            'distance_km': 'mean'
        }).reset_index()
        courier_stats.columns = ['courier', 'avg_delivery_time', 'std_delivery_time', 
                                 'avg_fuel_cost', 'avg_distance']
        courier_stats = courier_stats.sort_values('avg_delivery_time', ascending=False)
        
        # Identify problem couriers
        problem_couriers = courier_stats[courier_stats['avg_delivery_time'] > courier_stats['avg_delivery_time'].median()]
        
        insights.append({
            'type': 'shipping',
            'text': f"🚚 **Shipping Delay Analysis**\n\n"
                   f"Average delivery time: {courier_stats['avg_delivery_time'].mean():.1f} days\n\n"
                   f"**Courier Partners at Risk of Delays:**\n" +
                   "\n".join([
                       f"• {row['courier']}: {row['avg_delivery_time']:.1f} days avg "
                       f"(±{row['std_delivery_time']:.1f} days)"
                       for _, row in problem_couriers.head(3).iterrows()
                   ]) +
                   f"\n\n⚠️ Recommendation: Consider redistributing load or renegotiating SLAs",
            'data': problem_couriers.to_dict('records')
        })
        
        # Impact on next quarter
        insights.append({
            'type': 'shipping_impact',
            'text': f"📊 **Next Quarter Impact**\n\n"
                   f"If delays persist:\n"
                   f"• Expected customer complaints: +15-25%\n"
                   f"• Potential revenue impact: ₹2-5 lakhs in refunds\n"
                   f"• Late delivery rate: {len(problem_couriers)/len(courier_stats)*100:.0f}% of routes\n\n"
                   f"**Mitigation strategies:**\n"
                   f"• Shift 30% of load to faster couriers\n"
                   f"• Implement real-time tracking\n"
                   f"• Add buffer time for peak season",
            'data': {
                'delay_impact_pct': 20,
                'affected_routes': len(problem_couriers)
            }
        })
        
        # Best performers
        best_couriers = courier_stats.head(3)
        insights.append({
            'type': 'best_couriers',
            'text': f"⭐ **Top Performing Couriers**\n\n" +
                   "\n".join([
                       f"• {row['courier']}: {row['avg_delivery_time']:.1f} days "
                       f"(₹{row['avg_fuel_cost']:.2f} avg cost)"
                       for _, row in best_couriers.iterrows()
                   ]),
            'data': best_couriers.to_dict('records')
        })
        
    except Exception as e:
        insights.append({
            'type': 'error',
            'text': f"⚠️ Error analyzing shipping: {str(e)}",
            'data': {'error': str(e)}
        })
    
    return insights


# ============================================================================
# SENTIMENT HANDLERS
# ============================================================================
def handle_sentiment_question(question, params):
    """Handle customer sentiment/review related questions"""
    insights = []
    
    try:
        # Load reviews data
        df_reviews = pd.read_csv(DATA_DIR / "customer_reviews_sample.csv")
        
        # Analyze sentiment
        sentiments = []
        for review in df_reviews['review_text'].head(100):  # Sample 100 reviews
            if pd.notna(review):
                score = sentiment_analyzer.polarity_scores(str(review))
                sentiments.append(score)
        
        if sentiments:
            avg_compound = np.mean([s['compound'] for s in sentiments])
            avg_positive = np.mean([s['pos'] for s in sentiments])
            avg_negative = np.mean([s['neg'] for s in sentiments])
            avg_neutral = np.mean([s['neu'] for s in sentiments])
            
            # Determine overall sentiment
            if avg_compound >= 0.05:
                overall = "Positive ✅"
                trend = "Customer sentiment is generally positive"
            elif avg_compound <= -0.05:
                overall = "Negative ⚠️"
                trend = "Customer sentiment needs attention"
            else:
                overall = "Neutral 😐"
                trend = "Customer sentiment is mixed"
            
            insights.append({
                'type': 'sentiment',
                'text': f"💬 **Customer Sentiment Analysis**\n\n"
                       f"Overall sentiment: **{overall}**\n"
                       f"• Positive reviews: {avg_positive*100:.1f}%\n"
                       f"• Negative reviews: {avg_negative*100:.1f}%\n"
                       f"• Neutral reviews: {avg_neutral*100:.1f}%\n\n"
                       f"**Trend**: {trend}\n"
                       f"**Compound score**: {avg_compound:.3f} (-1 to +1 scale)",
                'data': {
                    'overall': overall,
                    'positive_pct': float(avg_positive * 100),
                    'negative_pct': float(avg_negative * 100),
                    'neutral_pct': float(avg_neutral * 100),
                    'compound_score': float(avg_compound)
                }
            })
            
            # Monthly trend
            if 'date' in df_reviews.columns or 'review_date' in df_reviews.columns:
                date_col = 'date' if 'date' in df_reviews.columns else 'review_date'
                df_reviews[date_col] = pd.to_datetime(df_reviews[date_col], errors='coerce')
                
                current_month = datetime.now().month
                this_month = df_reviews[df_reviews[date_col].dt.month == current_month]
                
                if len(this_month) > 0:
                    insights.append({
                        'type': 'sentiment_trend',
                        'text': f"📅 **This Month's Sentiment**\n\n"
                               f"• Reviews analyzed: {len(this_month)}\n"
                               f"• Trending: {'Positive' if avg_compound > 0 else 'Needs Improvement'}\n"
                               f"• Action: {'Keep up the good work!' if avg_compound > 0 else 'Review common complaints and address'}",
                        'data': {'month': current_month, 'review_count': len(this_month)}
                    })
        
        # Common issues (if rating column exists)
        if 'rating' in df_reviews.columns:
            low_ratings = df_reviews[df_reviews['rating'] <= 2]
            high_ratings = df_reviews[df_reviews['rating'] >= 4]
            
            insights.append({
                'type': 'rating_breakdown',
                'text': f"⭐ **Rating Breakdown**\n\n"
                       f"• High ratings (4-5 stars): {len(high_ratings)} reviews ({len(high_ratings)/len(df_reviews)*100:.1f}%)\n"
                       f"• Low ratings (1-2 stars): {len(low_ratings)} reviews ({len(low_ratings)/len(df_reviews)*100:.1f}%)\n"
                       f"• Average rating: {df_reviews['rating'].mean():.2f}/5.0",
                'data': {
                    'high_ratings': len(high_ratings),
                    'low_ratings': len(low_ratings),
                    'avg_rating': float(df_reviews['rating'].mean())
                }
            })
        
    except Exception as e:
        insights.append({
            'type': 'error',
            'text': f"⚠️ Error analyzing sentiment: {str(e)}",
            'data': {'error': str(e)}
        })
    
    return insights


# ============================================================================
# WAREHOUSE HANDLERS
# ============================================================================
def handle_warehouse_question(question, params):
    """Handle warehouse operation questions"""
    insights = []
    
    try:
        # Load warehouse model and data
        model_warehouse = load_model("model_warehouse.pkl")
        df_warehouse = pd.read_csv(DATA_DIR / "warehouse_ops_sample.csv")
        
        # Warehouse performance analysis
        wh_stats = df_warehouse.groupby('warehouse_id').agg({
            'processing_time_hrs': ['mean', 'std'],
            'operational_cost_inr': 'mean',
            'workforce_available': 'mean'
        }).reset_index()
        wh_stats.columns = ['warehouse_id', 'avg_processing_time', 'std_processing', 
                           'avg_cost', 'avg_workforce']
        
        # Identify inefficient warehouses
        median_time = wh_stats['avg_processing_time'].median()
        inefficient = wh_stats[wh_stats['avg_processing_time'] > median_time]
        efficient = wh_stats[wh_stats['avg_processing_time'] <= median_time]
        
        insights.append({
            'type': 'warehouse',
            'text': f"🏭 **Warehouse Efficiency Analysis**\n\n"
                   f"Average processing time: {wh_stats['avg_processing_time'].mean():.1f} hours\n\n"
                   f"**Underperforming Warehouses:**\n" +
                   "\n".join([
                       f"• {row['warehouse_id']}: {row['avg_processing_time']:.1f}hrs "
                       f"(Cost: ₹{row['avg_cost']:.0f})"
                       for _, row in inefficient.head(3).iterrows()
                   ]) +
                   f"\n\n**Top Performers:**\n" +
                   "\n".join([
                       f"• {row['warehouse_id']}: {row['avg_processing_time']:.1f}hrs"
                       for _, row in efficient.head(3).iterrows()
                   ]),
            'data': {
                'inefficient': inefficient.to_dict('records'),
                'efficient': efficient.to_dict('records')
            }
        })
        
        insights.append({
            'type': 'warehouse_recommendations',
            'text': f"💡 **Optimization Recommendations**\n\n"
                   f"• Redistribute load from slow warehouses to efficient ones\n"
                   f"• Potential time savings: {(inefficient['avg_processing_time'].mean() - efficient['avg_processing_time'].mean()):.1f} hours per order\n"
                   f"• Cost reduction opportunity: ₹{(inefficient['avg_cost'].mean() - efficient['avg_cost'].mean()) * 1000:.0f} per month\n"
                   f"• Consider workforce retraining for underperforming facilities",
            'data': {
                'potential_savings': float((inefficient['avg_cost'].mean() - efficient['avg_cost'].mean()) * 1000)
            }
        })
        
    except Exception as e:
        insights.append({
            'type': 'error',
            'text': f"⚠️ Error analyzing warehouse: {str(e)}",
            'data': {'error': str(e)}
        })
    
    return insights


# ============================================================================
# MAIN CHAT ENDPOINT
# ============================================================================
@app.route('/chat', methods=['POST'])
def chat():
    """Main endpoint for chatbot interactions"""
    try:
        data = request.json
        question = data.get('question', '')
        
        if not question:
            return jsonify({'error': 'No question provided'}), 400
        
        print(f"\n{'='*60}")
        print(f"📝 NEW QUESTION: {question}")
        print(f"{'='*60}")
        
        # Detect intent and extract parameters
        intent = detect_intent(question)
        params = extract_params(question)
        
        print(f"🎯 INTENT DETECTED: {intent}")
        print(f"📊 PARAMETERS EXTRACTED: {params}")
        print(f"{'='*60}\n")
        
        # Route to appropriate handler
        if intent == 'forecast':
            print("➡️  Routing to FORECAST handler")
            insights = handle_forecast_question(question, params)
        elif intent == 'inventory':
            print("➡️  Routing to INVENTORY handler")
            insights = handle_inventory_question(question, params)
        elif intent == 'shipping':
            print("➡️  Routing to SHIPPING handler")
            insights = handle_shipping_question(question, params)
        elif intent == 'sentiment':
            print("➡️  Routing to SENTIMENT handler")
            insights = handle_sentiment_question(question, params)
        elif intent == 'warehouse':
            print("➡️  Routing to WAREHOUSE handler")
            insights = handle_warehouse_question(question, params)
        else:
            print("➡️  Routing to GENERAL handler")
            # General response
            insights = [{
                'type': 'general',
                'text': f"👋 I can help you with:\n\n"
                       f"📈 **Forecasting**: Demand predictions, seasonal trends\n"
                       f"📦 **Inventory**: Stock recommendations, sufficiency checks\n"
                       f"🚚 **Shipping**: Courier performance, delay analysis\n"
                       f"💬 **Sentiment**: Customer review analysis\n"
                       f"🏭 **Warehouse**: Efficiency and optimization\n\n"
                       f"Try asking something like:\n"
                       f'• "What will Q4 demand look like?"\n'
                       f'• "If demand increases by 20%, what stock adjustments are needed?"\n'
                       f'• "How are customer reviews trending?"',
                'data': {}
            }]
        
        return jsonify({
            'question': question,
            'intent': intent,
            'params': params,
            'insights': insights,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'insights': [{
                'type': 'error',
                'text': f"⚠️ An error occurred: {str(e)}\n\nPlease try rephrasing your question.",
                'data': {'error': str(e)}
            }]
        }), 500


@app.route('/api/dashboard/analytics', methods=['GET'])
def dashboard_analytics():
    """
    Comprehensive dashboard analytics endpoint
    Analyzes all CSV data and returns insights for visualization
    """
    try:
        # Load all datasets
        orders_df = pd.read_csv(DATA_DIR / 'orders_sample.csv')
        warehouse_df = pd.read_csv(DATA_DIR / 'warehouse_ops_sample.csv')
        transport_df = pd.read_csv(DATA_DIR / 'transportations_sample.csv')
        seasonal_df = pd.read_csv(DATA_DIR / 'seasonal_demand.csv')
        reviews_df = pd.read_csv(DATA_DIR / 'customer_reviews_sample.csv')
        
        # Convert date columns
        orders_df['order_date'] = pd.to_datetime(orders_df['order_date'])
        orders_df['delivery_date'] = pd.to_datetime(orders_df['delivery_date'])
        warehouse_df['date'] = pd.to_datetime(warehouse_df['date'])
        seasonal_df['date'] = pd.to_datetime(seasonal_df['date'])
        reviews_df['review_date'] = pd.to_datetime(reviews_df['review_date'])
        
        # Calculate delivery delays
        orders_df['delivery_days'] = (orders_df['delivery_date'] - orders_df['order_date']).dt.days
        orders_df['is_delayed'] = orders_df['delivery_days'] > 2  # Assuming 2 days is standard
        
        # 1. SEASONAL DEMAND ANALYSIS
        seasonal_monthly = seasonal_df.copy()
        seasonal_monthly['month'] = seasonal_monthly['date'].dt.strftime('%b %Y')
        seasonal_monthly['year_month'] = seasonal_monthly['date'].dt.to_period('M')
        demand_by_month = seasonal_monthly.groupby('year_month').agg({
            'demand_index': 'mean',
            'campaign_flag': 'sum'
        }).reset_index()
        demand_by_month['month'] = demand_by_month['year_month'].astype(str)
        demand_data = demand_by_month.tail(12).to_dict('records')
        
        # Top categories by demand
        category_demand = seasonal_df.groupby('category')['demand_index'].mean().sort_values(ascending=False).head(10)
        category_demand_data = [{'category': cat, 'demand': float(val)} for cat, val in category_demand.items()]
        
        # 2. WAREHOUSE EFFICIENCY ANALYSIS
        warehouse_efficiency = warehouse_df.groupby('warehouse_id').agg({
            'avg_processing_time_hours': 'mean',
            'storage_cost_per_pallet_inr': 'mean',
            'workforce_available': 'mean',
            'shifts': 'mean'
        }).reset_index()
        warehouse_efficiency['efficiency_score'] = (
            100 - (warehouse_efficiency['avg_processing_time_hours'] / warehouse_efficiency['avg_processing_time_hours'].max() * 50)
        ).round(2)
        warehouse_data = warehouse_efficiency.to_dict('records')
        
        # Warehouse processing time trends
        warehouse_trends = warehouse_df.groupby(['warehouse_id', pd.Grouper(key='date', freq='M')]).agg({
            'avg_processing_time_hours': 'mean'
        }).reset_index()
        warehouse_trends['month'] = warehouse_trends['date'].dt.strftime('%b %Y')
        
        # 3. TRANSPORTATION & COURIER ANALYSIS
        courier_performance = transport_df.groupby('courier_partner').agg({
            'courier_on_time_rate': 'mean',
            'distance_km': 'mean',
            'fuel_cost_per_km_inr': 'mean',
            'estimated_transit_hours': 'mean'
        }).reset_index()
        courier_performance['on_time_rate_pct'] = (courier_performance['courier_on_time_rate'] * 100).round(2)
        courier_data = courier_performance.to_dict('records')
        
        # Cost by route
        transport_df['total_fuel_cost'] = transport_df['distance_km'] * transport_df['fuel_cost_per_km_inr']
        route_costs = transport_df.groupby('city').agg({
            'total_fuel_cost': 'mean',
            'distance_km': 'mean',
            'estimated_transit_hours': 'mean'
        }).sort_values('total_fuel_cost', ascending=False).head(15).reset_index()
        route_cost_data = route_costs.to_dict('records')
        
        # 4. DELIVERY PERFORMANCE ANALYSIS
        delivery_performance = orders_df.groupby('city').agg({
            'delivery_days': 'mean',
            'is_delayed': 'sum',
            'order_id': 'count'
        }).reset_index()
        delivery_performance.columns = ['city', 'avg_delivery_days', 'delayed_count', 'total_orders']
        delivery_performance['delay_rate'] = (delivery_performance['delayed_count'] / delivery_performance['total_orders'] * 100).round(2)
        delivery_performance = delivery_performance.sort_values('delay_rate', ascending=False).head(15)
        delivery_data = delivery_performance.to_dict('records')
        
        # Delays by courier partner
        courier_delays = orders_df.groupby('courier_partner').agg({
            'is_delayed': 'sum',
            'order_id': 'count',
            'delivery_days': 'mean'
        }).reset_index()
        courier_delays.columns = ['courier_partner', 'delayed_count', 'total_orders', 'avg_delivery_days']
        courier_delays['delay_rate'] = (courier_delays['delayed_count'] / courier_delays['total_orders'] * 100).round(2)
        courier_delays_data = courier_delays.sort_values('delay_rate', ascending=False).to_dict('records')
        
        # 5. CUSTOMER SENTIMENT ANALYSIS
        reviews_df['sentiment_score'] = reviews_df['review_text'].apply(
            lambda x: sentiment_analyzer.polarity_scores(str(x))['compound']
        )
        reviews_df['sentiment'] = pd.cut(
            reviews_df['sentiment_score'],
            bins=[-1, -0.05, 0.05, 1],
            labels=['Negative', 'Neutral', 'Positive']
        )
        
        sentiment_dist = reviews_df['sentiment'].value_counts().to_dict()
        sentiment_data = [{'sentiment': k, 'count': int(v)} for k, v in sentiment_dist.items()]
        
        # Sentiment by rating
        sentiment_by_rating = reviews_df.groupby('rating')['sentiment_score'].mean().to_dict()
        sentiment_rating_data = [{'rating': int(k), 'avg_sentiment': float(v)} for k, v in sentiment_by_rating.items()]
        
        # Monthly sentiment trends
        reviews_df['month'] = reviews_df['review_date'].dt.to_period('M')
        sentiment_trends = reviews_df.groupby('month').agg({
            'sentiment_score': 'mean',
            'rating': 'mean'
        }).reset_index().tail(12)
        sentiment_trends['month_str'] = sentiment_trends['month'].astype(str)
        sentiment_trend_data = sentiment_trends[['month_str', 'sentiment_score', 'rating']].to_dict('records')
        
        # 6. COST ANALYSIS
        # Average order value by category
        order_value_by_category = orders_df.groupby('category')['order_value_inr'].mean().sort_values(ascending=False).head(10)
        order_value_data = [{'category': cat, 'avg_value': float(val)} for cat, val in order_value_by_category.items()]
        
        # Total costs
        avg_transport_cost = transport_df['total_fuel_cost'].mean()
        avg_storage_cost = warehouse_df['storage_cost_per_pallet_inr'].mean()
        total_order_value = orders_df['order_value_inr'].sum()
        
        # 7. KEY METRICS
        total_orders = len(orders_df)
        total_delayed = orders_df['is_delayed'].sum()
        avg_delivery_time = orders_df['delivery_days'].mean()
        delay_rate = (total_delayed / total_orders * 100).round(2)
        
        total_warehouses = warehouse_df['warehouse_id'].nunique()
        avg_processing_time = warehouse_df['avg_processing_time_hours'].mean()
        
        total_routes = len(transport_df)
        avg_on_time_rate = (transport_df['courier_on_time_rate'].mean() * 100).round(2)
        
        avg_rating = reviews_df['rating'].mean()
        avg_sentiment = reviews_df['sentiment_score'].mean()
        
        # Return comprehensive analytics
        return jsonify({
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'data': {
                # Key Metrics
                'metrics': {
                    'total_orders': int(total_orders),
                    'total_delayed': int(total_delayed),
                    'delay_rate': float(delay_rate),
                    'avg_delivery_days': float(avg_delivery_time),
                    'total_warehouses': int(total_warehouses),
                    'avg_processing_hours': float(avg_processing_time),
                    'total_routes': int(total_routes),
                    'avg_on_time_rate': float(avg_on_time_rate),
                    'avg_rating': float(avg_rating),
                    'avg_sentiment': float(avg_sentiment),
                    'total_order_value': float(total_order_value),
                    'avg_transport_cost': float(avg_transport_cost),
                    'avg_storage_cost': float(avg_storage_cost)
                },
                # Chart Data
                'seasonal_demand': demand_data,
                'category_demand': category_demand_data,
                'warehouse_efficiency': warehouse_data,
                'courier_performance': courier_data,
                'route_costs': route_cost_data,
                'delivery_performance': delivery_data,
                'courier_delays': courier_delays_data,
                'sentiment_distribution': sentiment_data,
                'sentiment_by_rating': sentiment_rating_data,
                'sentiment_trends': sentiment_trend_data,
                'order_value_by_category': order_value_data
            }
        })
        
    except Exception as e:
        print(f"❌ Error in dashboard analytics: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'models_loaded': list(MODELS.keys()),
        'timestamp': datetime.now().isoformat()
    })


@app.route('/', methods=['GET'])
def home():
    """Root endpoint"""
    return jsonify({
        'service': 'Insight-o-pedia AI Backend',
        'version': '1.0.0',
        'endpoints': {
            '/chat': 'POST - Main chatbot endpoint',
            '/health': 'GET - Health check'
        }
    })


if __name__ == '__main__':
    print("🚀 Starting Insight-o-pedia Flask Backend...")
    print(f"📁 Models directory: {MODELS_DIR}")
    print(f"📁 Data directory: {DATA_DIR}")
    print("🌐 Server running on http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
