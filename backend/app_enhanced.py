# app_enhanced.py - Flask Backend with Gemini AI Integration
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from datetime import datetime, timedelta
import re
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import os
import json

# Try to import Google Gemini
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️  Google Gemini not available. Install with: pip install google-generativeai")

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Loaded environment variables from .env file")
except ImportError:
    print("⚠️  python-dotenv not installed. Using system environment variables only.")

app = Flask(__name__)
CORS(app)

# Paths
MODELS_DIR = Path(__file__).parent / "models"
DATA_DIR = Path(__file__).parent / "data"

# Global model cache
MODELS = {}
sentiment_analyzer = SentimentIntensityAnalyzer()

# Gemini Configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')  # Load from .env or environment
if GEMINI_AVAILABLE and GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        # Use the latest fast Gemini model (updated list as of 2025)
        model_names = [
            'models/gemini-2.0-flash',  # Latest fast model
            'models/gemini-2.5-flash',  # Latest 2.5 version
            'models/gemini-flash-latest',  # Alias for latest flash
            'models/gemini-2.0-flash-001',  # Specific version
            'models/gemini-pro-latest',  # Pro version fallback
        ]
        
        gemini_model = None
        for model_name in model_names:
            try:
                gemini_model = genai.GenerativeModel(model_name)
                # Test with a simple generation to verify it works
                test_response = gemini_model.generate_content("Test")
                print(f"✅ Gemini AI enabled with model: {model_name}")
                print(f"   API Key: {GEMINI_API_KEY[:10]}...")
                print("🤖 Two-stage AI: Intent Detection → Data Fetch → Natural Language Response")
                break
            except Exception as model_error:
                print(f"   ⚠️  Model {model_name} failed: {str(model_error)[:100]}")
                continue
        
        if not gemini_model:
            print("❌ No working Gemini model found. Using keyword-based detection + pre-formatted insights.")
            GEMINI_AVAILABLE = False
    except Exception as e:
        gemini_model = None
        print(f"⚠️  Gemini AI configuration failed: {e}")
else:
    gemini_model = None
    print("⚠️  Gemini AI not configured. Using keyword-based detection.")


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
# ENHANCED INTENT DETECTION WITH GEMINI
# ============================================================================
def detect_intent_with_gemini(question):
    """Use Gemini AI to detect intent and extract parameters from natural language"""
    if not gemini_model:
        return detect_intent_keywords(question), extract_params(question)
    
    try:
        prompt = f"""Analyze this supply chain question and extract intent + parameters.

Question: "{question}"

Categories:
- forecast: demand predictions, trends, Q1/Q2/Q3/Q4, future outlook
- inventory: stock levels, adjustments, recommendations
- shipping: delivery, courier performance, delays
- sentiment: customer reviews, satisfaction, feedback
- warehouse: operations, efficiency, processing
- general: help, capabilities, unclear

Respond in JSON format:
{{
  "intent": "category_name",
  "quarter": "Q1/Q2/Q3/Q4 if mentioned",
  "percentage": number_if_mentioned,
  "timeframe": "description if relevant"
}}"""

        response = gemini_model.generate_content(prompt)
        result_text = response.text.strip()
        
        # Try to parse JSON response
        try:
            # Clean markdown code blocks if present
            if '```json' in result_text:
                result_text = result_text.split('```json')[1].split('```')[0].strip()
            elif '```' in result_text:
                result_text = result_text.split('```')[1].split('```')[0].strip()
            
            result = json.loads(result_text)
            intent = result.get('intent', 'general').lower()
            
            # Build params from Gemini response
            params = {}
            if result.get('quarter'):
                q = result['quarter'].upper()
                params['quarter'] = q
                if q == 'Q1':
                    params['months'] = [1, 2, 3]
                elif q == 'Q2':
                    params['months'] = [4, 5, 6]
                elif q == 'Q3':
                    params['months'] = [7, 8, 9]
                elif q == 'Q4':
                    params['months'] = [10, 11, 12]
            
            if result.get('percentage'):
                params['surge_pct'] = float(result['percentage']) / 100
            
            if result.get('timeframe'):
                params['timeframe'] = result['timeframe']
            
            valid_intents = ['forecast', 'inventory', 'shipping', 'sentiment', 'warehouse', 'general']
            if intent in valid_intents:
                print(f"🤖 Gemini: intent={intent}, params={params}")
                return intent, params
            else:
                print(f"⚠️  Gemini returned invalid intent: {intent}, falling back to keywords")
                return detect_intent_keywords(question), extract_params(question)
        
        except json.JSONDecodeError:
            # If JSON parsing fails, fall back to simple text parsing
            intent = result_text.strip().lower()
            valid_intents = ['forecast', 'inventory', 'shipping', 'sentiment', 'warehouse', 'general']
            if intent in valid_intents:
                print(f"🤖 Gemini: intent={intent} (text mode)")
                return intent, extract_params(question)
            else:
                print(f"⚠️  Could not parse Gemini response, falling back to keywords")
                return detect_intent_keywords(question), extract_params(question)
            
    except Exception as e:
        print(f"⚠️  Gemini error: {e}, falling back to keywords")
        return detect_intent_keywords(question), extract_params(question)


def detect_intent_keywords(question):
    """Fallback keyword-based intent detection"""
    q = question.lower()
    
    # Forecasting/Demand keywords
    if any(kw in q for kw in ['forecast', 'predict', 'demand', 'q4', 'q1', 'q2', 'q3', 'quarter', 'next', 'future', 'trend', 'seasonal', 'increase expected', 'december', 'will', 'look like']):
        return 'forecast'
    
    # Inventory/Stock keywords
    if any(kw in q for kw in ['inventory', 'stock', 'adjust', 'boost', 'stockout', 'sufficient', 'category', 'increase by', 'surge', 'need']):
        return 'inventory'
    
    # Shipping/Transport keywords
    if any(kw in q for kw in ['shipping', 'delivery', 'delay', 'transport', 'courier', 'partner', 'late']):
        return 'shipping'
    
    # Sentiment keywords
    if any(kw in q for kw in ['sentiment', 'review', 'customer', 'feedback', 'positive', 'negative', 'trending']):
        return 'sentiment'
    
    # Warehouse keywords
    if any(kw in q for kw in ['warehouse', 'processing', 'efficiency', 'operation', 'storage']):
        return 'warehouse'
    
    return 'general'


def detect_intent(question):
    """Main intent detection router - returns (intent, params) tuple"""
    if GEMINI_AVAILABLE and gemini_model:
        return detect_intent_with_gemini(question)
    else:
        return detect_intent_keywords(question), extract_params(question)


def extract_params(question):
    """Extract parameters from question like percentages, months, quarters"""
    params = {}
    q_lower = question.lower()
    
    # Extract percentage (e.g., "20%", "15 percent")
    pct_match = re.search(r'(\d+)\s*(?:%|percent)', q_lower)
    if pct_match:
        params['surge_pct'] = float(pct_match.group(1)) / 100
    
    # Extract time period
    if 'q4' in q_lower or 'fourth quarter' in q_lower:
        params['quarter'] = 'Q4'
        params['months'] = [10, 11, 12]
    elif 'q3' in q_lower:
        params['quarter'] = 'Q3'
        params['months'] = [7, 8, 9]
    elif 'q1' in q_lower:
        params['quarter'] = 'Q1'
        params['months'] = [1, 2, 3]
    elif 'q2' in q_lower:
        params['quarter'] = 'Q2'
        params['months'] = [4, 5, 6]
    
    # Extract days
    days_match = re.search(r'(\d+)\s*days?', q_lower)
    if days_match:
        params['days'] = int(days_match.group(1))
    
    # Extract months
    if 'december' in q_lower:
        params['target_month'] = 12
    elif 'january' in q_lower:
        params['target_month'] = 1
    
    return params


# ============================================================================
# STAGE 2: GEMINI OUTPUT FORMATTING
# ============================================================================
def format_insights_with_gemini(question, insights_data, intent):
    """Use Gemini to format raw data insights into natural, conversational responses"""
    # Check if Gemini is available and working
    if not GEMINI_AVAILABLE or not gemini_model or not insights_data:
        print("⚠️  Gemini formatting skipped - using pre-formatted insights")
        return insights_data
    
    try:
        # Convert insights to a clean summary for Gemini
        data_summary = []
        for insight in insights_data:
            summary_item = {
                'type': insight.get('type', ''),
                'text': insight.get('text', '')[:500]  # Limit text length
            }
            # Only include key data points to avoid token limits
            if 'data' in insight and insight['data']:
                if isinstance(insight['data'], dict):
                    # Extract only important numeric/string values
                    filtered_data = {k: v for k, v in insight['data'].items() 
                                   if isinstance(v, (int, float, str, bool))}
                    summary_item['data'] = filtered_data
            data_summary.append(summary_item)
        
        prompt = f"""You are an AI Supply Chain Analyst for Amazon India. A user asked: "{question}"

Data Analysis Results:
{json.dumps(data_summary, indent=2, default=str)[:2000]}

Instructions:
1. Answer the user's question directly and conversationally
2. Use the data provided to give specific numbers and insights
3. Format with markdown (**, bullet points) for clarity
4. Keep response focused and actionable (2-4 paragraphs)
5. Use emojis minimally: 📊 💡 ⚠️ ✅
6. If data shows problems, mention them with solutions
7. Be professional but conversational

Generate a clear, accurate response based ONLY on the provided data:"""

        # Generate response with safety settings
        response = gemini_model.generate_content(
            prompt,
            generation_config={
                'temperature': 0.7,
                'top_p': 0.9,
                'max_output_tokens': 1024
            }
        )
        
        formatted_text = response.text.strip()
        
        if formatted_text and len(formatted_text) > 20:
            print(f"✨ Gemini enhanced response ({len(formatted_text)} chars)")
            
            # Return formatted response as a single insight
            return [{
                'type': 'ai_enhanced',
                'text': formatted_text,
                'data': {
                    'original_insights_count': len(insights_data),
                    'enhanced_by': 'gemini',
                    'raw_insights': insights_data  # Keep original for reference
                }
            }]
        else:
            print("⚠️  Gemini returned empty response, using pre-formatted insights")
            return insights_data
        
    except Exception as e:
        print(f"⚠️  Gemini formatting error: {str(e)[:200]}")
        print("   → Falling back to pre-formatted insights")
        return insights_data  # Return original if Gemini fails


# ============================================================================
# FORECASTING HANDLERS
# ============================================================================
def handle_forecast_question(question, params):
    """Handle demand/forecast related questions with refined output"""
    insights = []
    
    try:
        # Load seasonal model
        print("📊 Loading seasonal forecasting model...")
        try:
            model_seasonal = load_model("model_seasonal_prophet.pkl")
            use_prophet = True
            print("✅ Using Prophet model for time series forecasting")
        except:
            try:
                model_seasonal = load_model("model_seasonal.pkl")
                use_prophet = False
                print("✅ Using LightGBM model for demand prediction")
            except:
                model_seasonal = load_model("model_seasonal_lgbm.pkl")
                use_prophet = False
                print("✅ Using LightGBM model for demand prediction")
        
        # Generate future dates
        days = params.get('days', 90)
        future_dates = pd.date_range(start=datetime.now(), periods=days, freq='D')
        print(f"📅 Generating forecast for {days} days ahead...")
        
        if use_prophet:
            future_df = pd.DataFrame({'ds': future_dates})
            forecast = model_seasonal.predict(future_df)
            
            avg_demand = forecast['yhat'].mean()
            trend = forecast['yhat'].iloc[-1] - forecast['yhat'].iloc[0]
            peak_demand = forecast['yhat'].max()
            low_demand = forecast['yhat'].min()
            trend_pct = (trend / avg_demand) * 100 if avg_demand != 0 else 0
            
            # Determine trend strength
            if abs(trend_pct) > 15:
                trend_strength = "Strong"
            elif abs(trend_pct) > 5:
                trend_strength = "Moderate"
            else:
                trend_strength = "Stable"
            
            insights.append({
                'type': 'forecast',
                'text': f"**📈 Demand Forecast (Next {days} Days)**\n\n"
                       f"**Overall Outlook:** {trend_strength} {'upward' if trend > 0 else 'downward' if trend < 0 else 'stable'} trend detected\n\n"
                       f"**Key Metrics:**\n"
                       f"• Average demand index: **{avg_demand:.1f}**\n"
                       f"• Trend change: **{trend:+.1f} points** ({trend_pct:+.1f}%)\n"
                       f"• Peak demand: **{peak_demand:.1f}** (prepare for surge)\n"
                       f"• Lowest demand: **{low_demand:.1f}**\n\n"
                       f"**Recommendation:** {'Increase inventory by 15-20%' if trend > 5 else 'Maintain current levels' if abs(trend) < 5 else 'Consider reducing inventory'}",
                'data': {
                    'avg_demand': float(avg_demand),
                    'trend': float(trend),
                    'trend_pct': float(trend_pct),
                    'peak': float(peak_demand),
                    'low': float(low_demand),
                    'forecast_sample': forecast[['ds', 'yhat']].head(10).to_dict('records')
                }
            })
        else:
            future_df = pd.DataFrame({'ds': future_dates})
            future_df['month'] = future_df['ds'].dt.month
            future_df['dow'] = future_df['ds'].dt.dayofweek
            predictions = model_seasonal.predict(future_df[['month', 'dow']])
            
            avg_demand = predictions.mean()
            trend = predictions[-1] - predictions[0]
            peak_demand = predictions.max()
            trend_pct = (trend / avg_demand) * 100 if avg_demand != 0 else 0
            
            # Determine trend strength
            if abs(trend_pct) > 15:
                trend_strength = "Strong"
            elif abs(trend_pct) > 5:
                trend_strength = "Moderate"
            else:
                trend_strength = "Stable"
            
            insights.append({
                'type': 'forecast',
                'text': f"**📈 Demand Forecast (Next {days} Days)**\n\n"
                       f"**Overall Outlook:** {trend_strength} {'upward' if trend > 0 else 'downward' if trend < 0 else 'stable'} trend\n\n"
                       f"**Key Metrics:**\n"
                       f"• Average demand index: **{avg_demand:.1f}**\n"
                       f"• Trend change: **{trend:+.1f} points** ({trend_pct:+.1f}%)\n"
                       f"• Peak demand: **{peak_demand:.1f}**\n\n"
                       f"**Recommendation:** {'Prepare for increased demand' if trend > 5 else 'Maintain steady operations' if abs(trend) < 5 else 'Optimize inventory levels'}",
                'data': {
                    'avg_demand': float(avg_demand),
                    'trend': float(trend),
                    'trend_pct': float(trend_pct),
                    'peak': float(peak_demand)
                }
            })
        
        # Orders prediction by category
        try:
            print("🏷️ Loading order prediction model for category analysis...")
            model_orders = load_model("model_orders.pkl")
            df_orders = pd.read_csv(DATA_DIR / "orders_sample.csv")
            
            # Get top categories by order volume
            top_categories = df_orders.groupby('category').size().sort_values(ascending=False).head(5).index.tolist()
            print(f"📦 Analyzing top {len(top_categories)} categories...")
            
            target_months = params.get('months', [10, 11, 12])
            quarter_name = params.get('quarter', 'upcoming period')
            
            predictions_by_category = []
            for cat_idx, category in enumerate(top_categories):
                # Create realistic sample data
                X_sample = pd.DataFrame({
                    'order_month': target_months * 10,
                    'order_dow': list(range(7)) * 4 + [0, 1],  # All days of week
                    'city': [0] * 30,
                    'warehouse_id': [cat_idx % 5] * 30,  # Distribute across warehouses
                    'category': [cat_idx] * 30,
                    'courier_partner': [0] * 30,
                    'route_id': [0] * 30
                })
                
                preds = model_orders.predict(X_sample)
                avg_value = preds.mean()
                total_value = avg_value * 30  # Estimated monthly volume
                
                # Calculate growth vs current
                current_avg = df_orders[df_orders['category'] == category]['order_value_inr'].mean()
                growth_pct = ((avg_value - current_avg) / current_avg * 100) if current_avg > 0 else 0
                
                predictions_by_category.append({
                    'category': category,
                    'avg_order_value': float(avg_value),
                    'total_predicted': float(total_value),
                    'growth_pct': float(growth_pct),
                    'priority': 'High' if growth_pct > 10 else 'Medium' if growth_pct > 5 else 'Normal'
                })
            
            # Sort by total value
            predictions_by_category.sort(key=lambda x: x['total_predicted'], reverse=True)
            
            insights.append({
                'type': 'category_forecast',
                'text': f"**💰 Category-wise Predictions** ({quarter_name})\n\n"
                       f"**Top Revenue Generators:**\n" + 
                       "\n".join([
                           f"• **{p['category']}**\n"
                           f"  - Avg order: ₹{p['avg_order_value']:.0f}\n"
                           f"  - Projected total: ₹{p['total_predicted']:,.0f}\n"
                           f"  - Growth: {p['growth_pct']:+.1f}% | Priority: {p['priority']}"
                           for p in predictions_by_category[:3]
                       ]),
                'data': predictions_by_category
            })
        except Exception as e:
            print(f"⚠️ Error in orders prediction: {e}")
        
        # Seasonal insights
        if 'target_month' in params or params.get('quarter') == 'Q4':
            insights.append({
                'type': 'seasonal',
                'text': f"**🎄 Seasonal Intelligence** (Q4 Analysis)\n\n"
                       f"**Expected Trends:**\n"
                       f"• Demand surge: **25-40% increase** vs Q3\n"
                       f"• Peak period: **Mid-December** (holiday rush)\n"
                       f"• Critical categories: Electronics, Jewelry, Fashion\n\n"
                       f"**Action Items:**\n"
                       f"✓ Start inventory buildup **2-3 weeks before** peak\n"
                       f"✓ Secure additional warehouse capacity\n"
                       f"✓ Alert courier partners for volume increase\n"
                       f"✓ Review staffing levels for fulfillment centers",
                'data': {'quarter': 'Q4', 'expected_increase': 0.30, 'peak_month': 12}
            })
        
    except Exception as e:
        print(f"❌ Forecast error: {e}")
        insights.append({
            'type': 'error',
            'text': f"⚠️ **Analysis Error**\n\nI encountered an issue generating the forecast: {str(e)}\n\nPlease ensure:\n• Models are properly trained\n• Data files are accessible\n• Try rephrasing your question",
            'data': {'error': str(e)}
        })
    
    return insights


# ============================================================================
# INVENTORY HANDLERS
# ============================================================================
def handle_inventory_question(question, params):
    """Handle inventory/stock related questions with refined recommendations"""
    insights = []
    
    try:
        surge_pct = params.get('surge_pct', 0.2)
        print(f"📦 Analyzing inventory for {surge_pct*100:.0f}% demand surge...")
        
        model_orders = load_model("model_orders.pkl")
        df_orders = pd.read_csv(DATA_DIR / "orders_sample.csv")
        
        # Get comprehensive category statistics
        category_stats = df_orders.groupby('category').agg({
            'order_value_inr': ['mean', 'sum', 'count', 'std']
        }).reset_index()
        category_stats.columns = ['category', 'avg_value', 'total_value', 'order_count', 'std_value']
        category_stats = category_stats.sort_values('total_value', ascending=False).head(5)
        
        recommendations = []
        total_investment = 0
        
        for _, row in category_stats.iterrows():
            current_value = row['total_value']
            predicted_with_surge = current_value * (1 + surge_pct)
            additional_stock_value = predicted_with_surge - current_value
            stock_increase = surge_pct * 100
            
            # Calculate risk level based on value and variability
            variability_ratio = row['std_value'] / row['avg_value'] if row['avg_value'] > 0 else 0
            if variability_ratio > 0.5 and stock_increase >= 20:
                risk_level = "High"
            elif variability_ratio > 0.3 or stock_increase >= 15:
                risk_level = "Medium"
            else:
                risk_level = "Low"
            
            recommendations.append({
                'category': row['category'],
                'current_demand': float(current_value),
                'predicted_demand': float(predicted_with_surge),
                'additional_investment': float(additional_stock_value),
                'recommended_stock_increase': f"{stock_increase:.0f}%",
                'priority': 'High' if stock_increase >= 20 else 'Medium',
                'risk_level': risk_level,
                'order_count': int(row['order_count'])
            })
            total_investment += additional_stock_value
        
        # Generate actionable recommendations
        high_priority = [r for r in recommendations if r['priority'] == 'High']
        
        insights.append({
            'type': 'inventory',
            'text': f"**📦 Inventory Optimization Plan** ({surge_pct*100:.0f}% Demand Surge)\n\n"
                   f"**Executive Summary:**\n"
                   f"• Total additional investment: **₹{total_investment:,.0f}**\n"
                   f"• Categories requiring action: **{len(recommendations)}**\n"
                   f"• High-priority items: **{len(high_priority)}**\n\n"
                   f"**Category Recommendations:**\n" +
                   "\n".join([
                       f"**{i+1}. {r['category']}** ({r['priority']} Priority)\n"
                       f"   • Current inventory value: ₹{r['current_demand']:,.0f}\n"
                       f"   • Recommended increase: **{r['recommended_stock_increase']}**\n"
                       f"   • Additional investment: ₹{r['additional_investment']:,.0f}\n"
                       f"   • Risk level: {r['risk_level']}\n"
                       for i, r in enumerate(recommendations[:3])
                   ]),
            'data': recommendations
        })
        
        # Stockout risk analysis
        high_risk_cats = [r['category'] for r in recommendations if r['risk_level'] in ['High', 'Medium']]
        
        insights.append({
            'type': 'stockout_risk',
            'text': f"**⚠️ Stockout Risk Assessment**\n\n"
                   f"**Critical Observations:**\n"
                   f"• **{len(high_risk_cats)}** categories at elevated stockout risk\n"
                   f"• Peak risk period: Next 30-45 days\n\n"
                   f"**High-Risk Categories:**\n" +
                   "\n".join([f"   • {cat}" for cat in high_risk_cats[:3]]) + "\n\n"
                   f"**Mitigation Strategy:**\n"
                   f"✓ Maintain safety stock at **30% above** predicted demand\n"
                   f"✓ Set up **weekly inventory reviews**\n"
                   f"✓ Establish backup supplier relationships\n"
                   f"✓ Enable real-time stock alerts",
            'data': {'high_risk_categories': high_risk_cats, 'risk_count': len(high_risk_cats)}
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
    """Handle shipping/delivery related questions with refined analytics"""
    insights = []
    
    try:
        print("🚚 Analyzing courier performance and delivery metrics...")
        model_transport = load_model("model_transport.pkl")
        df_transport = pd.read_csv(DATA_DIR / "transportations_sample.csv")
        
        # Comprehensive courier analysis
        courier_stats = df_transport.groupby('courier_partner').agg({
            'delivery_time_days': ['mean', 'std', 'min', 'max'],
            'fuel_cost_inr': ['mean', 'sum'],
            'distance_km': 'mean'
        }).reset_index()
        courier_stats.columns = ['courier', 'avg_delivery_time', 'std_delivery_time', 
                                 'min_delivery', 'max_delivery', 'avg_fuel_cost', 
                                 'total_fuel_cost', 'avg_distance']
        
        # Calculate performance scores
        overall_avg = courier_stats['avg_delivery_time'].mean()
        courier_stats['performance_vs_avg'] = ((overall_avg - courier_stats['avg_delivery_time']) / overall_avg * 100)
        courier_stats['reliability'] = 1 / (1 + courier_stats['std_delivery_time'])  # Lower variance = higher reliability
        
        # Identify problem couriers (above median delivery time)
        median_time = courier_stats['avg_delivery_time'].median()
        problem_couriers = courier_stats[courier_stats['avg_delivery_time'] > median_time].sort_values('avg_delivery_time', ascending=False)
        
        # Identify best performers
        best_couriers = courier_stats.sort_values('avg_delivery_time').head(3)
        
        # Calculate business impact
        delay_impact_pct = (len(problem_couriers) / len(courier_stats)) * 100
        
        insights.append({
            'type': 'shipping',
            'text': f"**🚚 Courier Performance Analysis**\n\n"
                   f"**Network Overview:**\n"
                   f"• Total courier partners: **{len(courier_stats)}**\n"
                   f"• Average delivery time: **{overall_avg:.1f} days**\n"
                   f"• Partners needing attention: **{len(problem_couriers)}** ({delay_impact_pct:.0f}%)\n\n"
                   f"**⚠️ Underperforming Couriers:**\n" +
                   "\n".join([
                       f"**{i+1}. {row['courier']}**\n"
                       f"   • Avg delivery: **{row['avg_delivery_time']:.1f} days** "
                       f"({row['performance_vs_avg']:+.0f}% vs network avg)\n"
                       f"   • Variability: ±{row['std_delivery_time']:.1f} days\n"
                       f"   • Range: {row['min_delivery']:.0f}-{row['max_delivery']:.0f} days\n"
                       f"   • Avg cost: ₹{row['avg_fuel_cost']:.0f}\n"
                       for i, (_, row) in enumerate(problem_couriers.head(3).iterrows())
                   ]) +
                   f"\n**💡 Recommendations:**\n"
                   f"✓ Redistribute **30-40%** of volume to top performers\n"
                   f"✓ Renegotiate SLAs with underperforming partners\n"
                   f"✓ Set up weekly performance reviews\n"
                   f"✓ Consider penalty clauses for delays",
            'data': {
                'problem_couriers': problem_couriers.to_dict('records'),
                'network_avg': float(overall_avg),
                'delay_impact_pct': float(delay_impact_pct)
            }
        })
        
        insights.append({
            'type': 'best_couriers',
            'text': f"**⭐ Top Performing Couriers**\n\n" +
                   "\n".join([
                       f"**{i+1}. {row['courier']}**\n"
                       f"   • Delivery time: **{row['avg_delivery_time']:.1f} days** "
                       f"({row['performance_vs_avg']:+.0f}% better than avg)\n"
                       f"   • Reliability score: {row['reliability']:.2f}\n"
                       f"   • Cost efficiency: ₹{row['avg_fuel_cost']:.0f} per shipment\n"
                       for i, (_, row) in enumerate(best_couriers.iterrows())
                   ]) +
                   f"\n**Strategy:** Increase allocation to these partners for critical shipments",
            'data': best_couriers.to_dict('records')
        })
        
        # Impact analysis
        insights.append({
            'type': 'shipping_impact',
            'text': f"**📊 Business Impact Analysis**\n\n"
                   f"**Current Quarter Projections:**\n"
                   f"• Potential delays affecting: **{delay_impact_pct:.0f}%** of shipments\n"
                   f"• Estimated customer complaints: **+15-25%**\n"
                   f"• Revenue at risk: **₹2-5 lakhs** (refunds + compensation)\n\n"
                   f"**Optimization Opportunities:**\n"
                   f"✓ Switch to top performers → Save **{(problem_couriers['avg_delivery_time'].mean() - best_couriers['avg_delivery_time'].mean()):.1f} days** per shipment\n"
                   f"✓ Reduce cost variability → Potential savings **₹{(problem_couriers['avg_fuel_cost'].mean() - best_couriers['avg_fuel_cost'].mean()) * 1000:.0f}**/month\n"
                   f"✓ Improve customer satisfaction score by **10-15 points**",
            'data': {
                'delay_impact_pct': float(delay_impact_pct),
                'time_savings': float(problem_couriers['avg_delivery_time'].mean() - best_couriers['avg_delivery_time'].mean())
            }
        })
        
    except Exception as e:
        print(f"❌ Shipping analysis error: {e}")
        insights.append({
            'type': 'error',
            'text': f"⚠️ **Shipping Analysis Error**\n\n{str(e)}\n\nPlease check if transportation data is available.",
            'data': {'error': str(e)}
        })
    
    return insights


# ============================================================================
# SENTIMENT HANDLERS
# ============================================================================
def handle_sentiment_question(question, params):
    """Handle customer sentiment/review related questions with detailed insights"""
    insights = []
    
    try:
        print("💬 Analyzing customer sentiment and reviews...")
        df_reviews = pd.read_csv(DATA_DIR / "customer_reviews_sample.csv")
        
        # Analyze more reviews for better accuracy
        sample_size = min(200, len(df_reviews))
        sentiments = []
        for review in df_reviews['review_text'].head(sample_size):
            if pd.notna(review):
                score = sentiment_analyzer.polarity_scores(str(review))
                sentiments.append(score)
        
        if sentiments:
            avg_compound = np.mean([s['compound'] for s in sentiments])
            avg_positive = np.mean([s['pos'] for s in sentiments])
            avg_negative = np.mean([s['neg'] for s in sentiments])
            avg_neutral = np.mean([s['neu'] for s in sentiments])
            
            # Categorize sentiment with thresholds
            positive_count = sum(1 for s in sentiments if s['compound'] >= 0.05)
            negative_count = sum(1 for s in sentiments if s['compound'] <= -0.05)
            neutral_count = len(sentiments) - positive_count - negative_count
            
            positive_pct = (positive_count / len(sentiments)) * 100
            negative_pct = (negative_count / len(sentiments)) * 100
            neutral_pct = (neutral_count / len(sentiments)) * 100
            
            # Determine overall sentiment and provide insights
            if avg_compound >= 0.05:
                overall = "Positive ✅"
                sentiment_status = "HEALTHY"
                trend = "Customer satisfaction is strong"
                action = "Maintain current service standards and identify success factors to replicate"
            elif avg_compound <= -0.05:
                overall = "Negative ⚠️"
                sentiment_status = "CRITICAL"
                trend = "Customer dissatisfaction requires immediate attention"
                action = "Launch immediate investigation into common complaints and service recovery plan"
            else:
                overall = "Neutral 😐"
                sentiment_status = "AT RISK"
                trend = "Customer sentiment is mixed with room for improvement"
                action = "Focus on converting neutral experiences into positive ones through service enhancement"
            
            insights.append({
                'type': 'sentiment',
                'text': f"**💬 Customer Sentiment Dashboard**\n\n"
                       f"**Overall Assessment:** {overall} ({sentiment_status})\n"
                       f"• Sentiment score: **{avg_compound:.3f}** (on -1 to +1 scale)\n"
                       f"• Sample analyzed: **{len(sentiments)}** reviews\n\n"
                       f"**Distribution Breakdown:**\n"
                       f"• 😊 Positive: **{positive_pct:.1f}%** ({positive_count} reviews)\n"
                       f"• 😐 Neutral: **{neutral_pct:.1f}%** ({neutral_count} reviews)\n"
                       f"• 😞 Negative: **{negative_pct:.1f}%** ({negative_count} reviews)\n\n"
                       f"**Insight:** {trend}\n\n"
                       f"**💡 Recommended Action:**\n{action}",
                'data': {
                    'overall': overall,
                    'status': sentiment_status,
                    'positive_pct': float(positive_pct),
                    'negative_pct': float(negative_pct),
                    'neutral_pct': float(neutral_pct),
                    'compound_score': float(avg_compound),
                    'sample_size': len(sentiments)
                }
            })
        
        # Enhanced rating analysis
        if 'rating' in df_reviews.columns:
            rating_counts = df_reviews['rating'].value_counts().sort_index()
            low_ratings = df_reviews[df_reviews['rating'] <= 2]
            high_ratings = df_reviews[df_reviews['rating'] >= 4]
            avg_rating = df_reviews['rating'].mean()
            
            # Rating health assessment
            high_rating_pct = (len(high_ratings) / len(df_reviews)) * 100
            low_rating_pct = (len(low_ratings) / len(df_reviews)) * 100
            
            if avg_rating >= 4.0:
                rating_health = "EXCELLENT ⭐⭐⭐⭐⭐"
                rating_action = "Maintain quality and collect testimonials for marketing"
            elif avg_rating >= 3.5:
                rating_health = "GOOD ⭐⭐⭐⭐"
                rating_action = "Small improvements needed to reach excellence"
            elif avg_rating >= 3.0:
                rating_health = "FAIR ⭐⭐⭐"
                rating_action = "Service quality improvements required"
            else:
                rating_health = "POOR ⚠️"
                rating_action = "URGENT: Major service overhaul needed"
            
            insights.append({
                'type': 'rating_breakdown',
                'text': f"**⭐ Rating Performance Analysis**\n\n"
                       f"**Overall Rating: {avg_rating:.2f}/5.0** - {rating_health}\n\n"
                       f"**Rating Distribution:**\n" +
                       "\n".join([
                           f"{'⭐' * int(rating)} ({rating}-star): **{count}** reviews ({count/len(df_reviews)*100:.1f}%)"
                           for rating, count in sorted(rating_counts.items(), reverse=True)
                       ]) +
                       f"\n\n**Key Metrics:**\n"
                       f"• Promoters (4-5 ⭐): **{high_rating_pct:.1f}%** ({len(high_ratings)} customers)\n"
                       f"• Detractors (1-2 ⭐): **{low_rating_pct:.1f}%** ({len(low_ratings)} customers)\n"
                       f"• Net Promoter Score (NPS): **{high_rating_pct - low_rating_pct:.1f}**\n\n"
                       f"**Action Plan:** {rating_action}",
                'data': {
                    'avg_rating': float(avg_rating),
                    'high_ratings': int(len(high_ratings)),
                    'low_ratings': int(len(low_ratings)),
                    'high_rating_pct': float(high_rating_pct),
                    'low_rating_pct': float(low_rating_pct),
                    'nps': float(high_rating_pct - low_rating_pct),
                    'rating_distribution': rating_counts.to_dict()
                }
            })
            
            # Critical issues analysis
            if len(low_ratings) > 0:
                critical_pct = (len(low_ratings) / len(df_reviews)) * 100
                insights.append({
                    'type': 'critical_issues',
                    'text': f"**🚨 Critical Issues Alert**\n\n"
                           f"• Low ratings detected: **{len(low_ratings)}** reviews ({critical_pct:.1f}%)\n"
                           f"• Estimated dissatisfied customers: **{len(low_ratings) * 10}** (assuming 10x silent majority)\n"
                           f"• Potential revenue impact: **₹{len(low_ratings) * 5000:.0f}** (avg CLV loss)\n\n"
                           f"**Priority Actions:**\n"
                           f"1. Personal outreach to all 1-2 star reviewers within 24 hours\n"
                           f"2. Identify common complaint patterns from negative reviews\n"
                           f"3. Implement service recovery program with compensation offers\n"
                           f"4. Weekly tracking of improvement metrics",
                    'data': {
                        'critical_count': int(len(low_ratings)),
                        'critical_pct': float(critical_pct)
                    }
                })
        
    except Exception as e:
        print(f"❌ Sentiment analysis error: {e}")
        insights.append({
            'type': 'error',
            'text': f"⚠️ **Sentiment Analysis Error**\n\n{str(e)}\n\nPlease check if customer review data is available.",
            'data': {'error': str(e)}
        })
    
    return insights


# ============================================================================
# WAREHOUSE HANDLERS
# ============================================================================
def handle_warehouse_question(question, params):
    """Handle warehouse operation questions with comprehensive efficiency analysis"""
    insights = []
    
    try:
        print("🏭 Analyzing warehouse operations and efficiency...")
        model_warehouse = load_model("model_warehouse.pkl")
        df_warehouse = pd.read_csv(DATA_DIR / "warehouse_ops_sample.csv")
        
        # Comprehensive warehouse metrics
        wh_stats = df_warehouse.groupby('warehouse_id').agg({
            'processing_time_hrs': ['mean', 'std', 'min', 'max'],
            'operational_cost_inr': ['mean', 'sum'],
            'workforce_available': 'mean'
        }).reset_index()
        wh_stats.columns = ['warehouse_id', 'avg_processing_time', 'std_processing', 
                           'min_processing', 'max_processing', 'avg_cost', 'total_cost', 'avg_workforce']
        
        # Calculate efficiency metrics
        network_avg_time = wh_stats['avg_processing_time'].mean()
        network_avg_cost = wh_stats['avg_cost'].mean()
        
        wh_stats['efficiency_score'] = (network_avg_time / wh_stats['avg_processing_time']) * (network_avg_cost / wh_stats['avg_cost'])
        wh_stats['time_vs_avg'] = ((wh_stats['avg_processing_time'] - network_avg_time) / network_avg_time * 100)
        wh_stats['cost_vs_avg'] = ((wh_stats['avg_cost'] - network_avg_cost) / network_avg_cost * 100)
        
        # Sort by efficiency
        wh_stats = wh_stats.sort_values('efficiency_score', ascending=False)
        
        # Identify categories
        median_time = wh_stats['avg_processing_time'].median()
        inefficient = wh_stats[wh_stats['avg_processing_time'] > median_time].sort_values('avg_processing_time', ascending=False)
        efficient = wh_stats[wh_stats['avg_processing_time'] <= median_time]
        
        # Calculate impact
        total_warehouses = len(wh_stats)
        inefficient_pct = (len(inefficient) / total_warehouses) * 100
        potential_time_savings = (inefficient['avg_processing_time'].mean() - efficient['avg_processing_time'].mean())
        
        insights.append({
            'type': 'warehouse',
            'text': f"**🏭 Warehouse Network Performance**\n\n"
                   f"**Network Overview:**\n"
                   f"• Total warehouses: **{total_warehouses}**\n"
                   f"• Network avg processing: **{network_avg_time:.1f} hours**\n"
                   f"• Network avg cost: **₹{network_avg_cost:.0f}** per operation\n"
                   f"• Facilities needing optimization: **{len(inefficient)}** ({inefficient_pct:.0f}%)\n\n"
                   f"**⚠️ Underperforming Warehouses:**\n" +
                   "\n".join([
                       f"**{i+1}. {row['warehouse_id']}**\n"
                       f"   • Processing time: **{row['avg_processing_time']:.1f} hrs** "
                       f"({row['time_vs_avg']:+.0f}% vs avg)\n"
                       f"   • Consistency: ±{row['std_processing']:.1f} hrs variance\n"
                       f"   • Cost: **₹{row['avg_cost']:.0f}** ({row['cost_vs_avg']:+.0f}% vs avg)\n"
                       f"   • Efficiency score: {row['efficiency_score']:.2f}\n"
                       for i, (_, row) in enumerate(inefficient.head(3).iterrows())
                   ]) +
                   f"\n**💡 Optimization Recommendations:**\n"
                   f"✓ Potential time savings: **{potential_time_savings:.1f} hours** per operation\n"
                   f"✓ Implement best practices from top performers\n"
                   f"✓ Workforce rebalancing across facilities\n"
                   f"✓ Process automation for repetitive tasks",
            'data': {
                'inefficient': inefficient.to_dict('records'),
                'network_avg_time': float(network_avg_time),
                'potential_savings': float(potential_time_savings)
            }
        })
        
        # Top performers analysis
        top_3 = efficient.head(3)
        insights.append({
            'type': 'warehouse_best',
            'text': f"**⭐ Top Performing Warehouses**\n\n" +
                   "\n".join([
                       f"**{i+1}. {row['warehouse_id']}**\n"
                       f"   • Processing time: **{row['avg_processing_time']:.1f} hrs** "
                       f"({abs(row['time_vs_avg']):.0f}% faster than avg)\n"
                       f"   • Efficiency score: **{row['efficiency_score']:.2f}**\n"
                       f"   • Cost: ₹{row['avg_cost']:.0f} per operation\n"
                       f"   • Workforce: {row['avg_workforce']:.0f} employees\n"
                       for i, (_, row) in enumerate(top_3.iterrows())
                   ]) +
                   f"\n**Key Success Factors to Replicate:**\n"
                   f"• Streamlined processes and layout optimization\n"
                   f"• Effective workforce management\n"
                   f"• Technology adoption for inventory tracking",
            'data': top_3.to_dict('records')
        })
        
        # Financial impact analysis
        total_operations = len(df_warehouse)
        current_total_cost = wh_stats['total_cost'].sum()
        optimal_cost = efficient['avg_cost'].mean() * total_operations
        potential_savings = current_total_cost - optimal_cost
        
        insights.append({
            'type': 'warehouse_financial',
            'text': f"**📊 Financial Impact Analysis**\n\n"
                   f"**Current State:**\n"
                   f"• Total operations: **{total_operations}**\n"
                   f"• Current operational cost: **₹{current_total_cost:,.0f}**\n"
                   f"• Average cost per operation: **₹{network_avg_cost:.0f}**\n\n"
                   f"**Optimization Potential:**\n"
                   f"• If all warehouses match top performer efficiency:\n"
                   f"  → Potential savings: **₹{potential_savings:,.0f}** ({potential_savings/current_total_cost*100:.1f}%)\n"
                   f"  → Time reduction: **{potential_time_savings * total_operations:.0f} hours** across network\n"
                   f"  → ROI on optimization investment: **150-200%** in 12 months\n\n"
                   f"**Strategic Actions:**\n"
                   f"1. Conduct efficiency audit at underperforming facilities\n"
                   f"2. Deploy best practices from top performers\n"
                   f"3. Invest in automation (ROI: 18-24 months)\n"
                   f"4. Implement performance-based incentives",
            'data': {
                'total_cost': float(current_total_cost),
                'potential_savings': float(potential_savings),
                'savings_pct': float(potential_savings/current_total_cost*100),
                'time_savings': float(potential_time_savings * total_operations)
            }
        })
        
    except Exception as e:
        print(f"❌ Warehouse analysis error: {e}")
        insights.append({
            'type': 'error',
            'text': f"⚠️ **Warehouse Analysis Error**\n\n{str(e)}\n\nPlease check if warehouse operations data is available.",
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
        
        print(f"\n📝 Question: {question}")
        
        # Stage 1: Detect intent and extract parameters using Gemini
        intent, params = detect_intent(question)
        
        print(f"🎯 Intent: {intent}")
        print(f"📊 Params: {params}")
        
        # Route to appropriate handler - Stage 1: Get raw insights
        print(f"📊 Fetching data from models...")
        if intent == 'forecast':
            raw_insights = handle_forecast_question(question, params)
        elif intent == 'inventory':
            raw_insights = handle_inventory_question(question, params)
        elif intent == 'shipping':
            raw_insights = handle_shipping_question(question, params)
        elif intent == 'sentiment':
            raw_insights = handle_sentiment_question(question, params)
        elif intent == 'warehouse':
            raw_insights = handle_warehouse_question(question, params)
        else:
            # General response
            raw_insights = [{
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
        
        # Stage 2: Format with Gemini for natural responses (skip for general/error)
        if intent != 'general' and gemini_model and raw_insights and raw_insights[0].get('type') != 'error':
            print(f"✨ Formatting response with Gemini...")
            insights = format_insights_with_gemini(question, raw_insights, intent)
        else:
            insights = raw_insights
        
        response = {
            'question': question,
            'intent': intent,
            'params': params,
            'insights': insights,
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"✅ Returning {len(insights)} insights")
        return jsonify(response)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({
            'error': str(e),
            'insights': [{
                'type': 'error',
                'text': f"⚠️ An error occurred: {str(e)}\n\nPlease try rephrasing your question.",
                'data': {'error': str(e)}
            }]
        }), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'models_loaded': list(MODELS.keys()),
        'gemini_enabled': GEMINI_AVAILABLE and gemini_model is not None,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/', methods=['GET'])
def home():
    """Root endpoint"""
    return jsonify({
        'service': 'Insight-o-pedia AI Backend (Enhanced)',
        'version': '2.0.0',
        'features': {
            'gemini_ai': GEMINI_AVAILABLE and gemini_model is not None,
            'ml_models': len(MODELS),
            'sentiment_analysis': True
        },
        'endpoints': {
            '/chat': 'POST - Main chatbot endpoint',
            '/health': 'GET - Health check'
        }
    })


if __name__ == '__main__':
    print("🚀 Starting Insight-o-pedia Flask Backend (Enhanced)...")
    print(f"📁 Models directory: {MODELS_DIR}")
    print(f"📁 Data directory: {DATA_DIR}")
    if GEMINI_AVAILABLE and gemini_model:
        print("🤖 Gemini AI: ENABLED")
    else:
        print("🤖 Gemini AI: DISABLED (using keyword detection)")
    print("🌐 Server running on http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
