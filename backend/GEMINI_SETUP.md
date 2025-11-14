# 🤖 Using Google Gemini AI for Better Intent Detection

The enhanced backend (`app_enhanced.py`) can use Google's Gemini AI to better understand user questions instead of simple keyword matching.

---

## 🎯 Why Use Gemini?

### Keyword Matching Problems:
- ❌ "Show me what's coming next quarter" → Doesn't match "Q4" or "quarter" keywords
- ❌ "Need more products for holidays" → Doesn't match "inventory" or "stock"
- ❌ "Which delivery company is slow?" → Doesn't match "courier" or "delay"

### Gemini AI Solution:
- ✅ Understands natural language variations
- ✅ Recognizes intent from context
- ✅ Handles typos and colloquialisms
- ✅ Better accuracy than keywords

---

## 🚀 Setup (Free - 60 requests/minute)

### Step 1: Get API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click **"Get API Key"**
3. Create new API key or use existing
4. Copy the key (looks like: `AIzaSy...`)

### Step 2: Install Gemini Library

```bash
cd backend
source venv/bin/activate
pip install google-generativeai
```

### Step 3: Set API Key

**Option A: Environment Variable (Recommended)**
```bash
export GEMINI_API_KEY='your-api-key-here'
```

**Option B: .env File**
```bash
# Create .env file in backend/
echo "GEMINI_API_KEY=your-api-key-here" > .env
```

Then install python-dotenv:
```bash
pip install python-dotenv
```

And add to app_enhanced.py:
```python
from dotenv import load_dotenv
load_dotenv()  # Add this before genai.configure()
```

**Option C: Hardcode (Not recommended for production)**
```python
# In app_enhanced.py, line 31
GEMINI_API_KEY = 'your-api-key-here'
```

### Step 4: Use Enhanced Backend

```bash
# Instead of app.py, run:
source venv/bin/activate
python app_enhanced.py
```

---

## 📊 Comparison

### Original app.py (Keyword Matching)
```python
Question: "What are we expecting in the last quarter?"
Keywords checked: ['q4', 'quarter', 'forecast', 'predict']
Result: ❌ No match → Returns GENERAL response
```

### app_enhanced.py (Gemini AI)
```python
Question: "What are we expecting in the last quarter?"
Gemini understands: "last quarter" = Q4 = forecasting
Result: ✅ Correct → Returns FORECAST insights
```

---

## 🎯 Test Examples

### Test 1: Vague Phrasing
```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What should we prepare for the holidays?"}'

# Keyword: ❌ GENERAL (no keywords matched)
# Gemini: ✅ FORECAST (understands holiday = December = Q4)
```

### Test 2: Colloquial Language
```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "Do we have enough stuff if sales go up?"}'

# Keyword: ❌ GENERAL
# Gemini: ✅ INVENTORY (stuff = stock, sales = demand)
```

### Test 3: Alternate Phrasing
```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "Which delivery service is taking too long?"}'

# Keyword: ❌ Maybe GENERAL
# Gemini: ✅ SHIPPING (delivery service = courier, too long = delay)
```

---

## 🔄 Switching Between Versions

### Use Original (Keyword Matching)
```bash
python app.py
```
- ✅ No API key needed
- ✅ Fast (no external calls)
- ❌ Limited understanding
- ❌ Requires exact keywords

### Use Enhanced (Gemini AI)
```bash
export GEMINI_API_KEY='your-key'
python app_enhanced.py
```
- ✅ Better understanding
- ✅ Natural language
- ✅ Handles variations
- ❌ Requires API key
- ❌ Slight latency (~200ms)

---

## 🧪 Testing Enhanced Version

### Start Enhanced Backend
```bash
cd backend
source venv/bin/activate
export GEMINI_API_KEY='your-api-key-here'
python app_enhanced.py
```

### Test Questions
Try these in your frontend:

1. **"What's coming next quarter?"**
   - Keyword: GENERAL ❌
   - Gemini: FORECAST ✅

2. **"Do we need more stuff for the big sale?"**
   - Keyword: GENERAL ❌
   - Gemini: INVENTORY ✅

3. **"Are customers happy?"**
   - Keyword: CUSTOMER match → but not in keywords ❌
   - Gemini: SENTIMENT ✅

4. **"Which warehouse is slow?"**
   - Keyword: WAREHOUSE ✅
   - Gemini: WAREHOUSE ✅

---

## 📈 Performance

### Free Tier Limits
- ✅ 60 requests per minute
- ✅ More than enough for demo
- ✅ No credit card required

### Response Time
- Keyword: ~50ms
- Gemini: ~250ms
- Total: Still under 500ms ✅

---

## 🎬 For Hackathon Demo

### If You Have Time (Recommended)
Use `app_enhanced.py` with Gemini:
- Shows advanced AI integration
- Better user experience
- Handles any question phrasing

### If No Time (Fallback)
Use `app.py` with keywords:
- Still works well
- No setup needed
- Just use exact keywords in demo questions

---

## 🔧 Troubleshooting

### "Gemini not available"
```bash
pip install google-generativeai
```

### "API key not configured"
```bash
export GEMINI_API_KEY='your-key'
# Or check .env file exists
```

### "Invalid API key"
- Get new key from [Google AI Studio](https://makersuite.google.com/app/apikey)
- Make sure no extra spaces
- Use single quotes: `'key'` not `"key"`

### "Quota exceeded"
- Free tier: 60 req/min
- Wait a minute and retry
- Or use original app.py

---

## 💡 Best of Both Worlds

Add fallback in `app_enhanced.py` (already included):
```python
def detect_intent(question):
    if gemini_model:
        try:
            return detect_intent_with_gemini(question)
        except:
            return detect_intent_keywords(question)  # Fallback
    else:
        return detect_intent_keywords(question)
```

This way:
- ✅ Uses Gemini when available
- ✅ Falls back to keywords if error
- ✅ Always works!

---

## 🎯 Recommendation

**For Hackathon:**
1. Start with `app.py` (keyword) - guaranteed to work
2. Test with your demo questions
3. If you have 10 minutes, setup Gemini
4. Test `app_enhanced.py`
5. Use whichever works better for you

**After Hackathon:**
- Deploy with Gemini for production
- Better user experience
- More flexible

---

## 📝 Quick Setup Checklist

- [ ] Get Gemini API key from Google AI Studio
- [ ] Install: `pip install google-generativeai`
- [ ] Set: `export GEMINI_API_KEY='your-key'`
- [ ] Run: `python app_enhanced.py`
- [ ] Test with vague questions
- [ ] Check terminal for "🤖 Gemini detected intent: ..."
- [ ] If working, use for demo!

---

Built for **NextGenHackathon 2025** 🚀
