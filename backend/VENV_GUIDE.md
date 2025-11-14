# 🚀 Quick Start - Virtual Environment

## Using Virtual Environment

The backend now uses a Python virtual environment (`venv`) to manage dependencies.

---

## ⚡ Quick Commands

### Start Backend Server

```bash
cd backend
source venv/bin/activate
python app.py
```

Or use the start script:

```bash
cd backend
./start.sh
```

---

## 🔧 Setup (First Time)

### 1. Create Virtual Environment

```bash
cd backend
python3 -m venv venv
```

### 2. Activate Virtual Environment

```bash
# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Train Models

```bash
python train.py orders 5000
python train.py seasonal 5000
python train.py warehouse 5000
python train.py transport 5000
python train.py reviews 5000
```

### 5. Start Server

```bash
python app.py
```

---

## 📋 Useful Commands

### Activate venv (Quick)

```bash
cd backend
source activate.sh
```

### Check Python Path

```bash
which python
# Should show: .../backend/venv/bin/python
```

### Check Installed Packages

```bash
pip list
```

### Update Dependencies

```bash
pip install -r requirements.txt --upgrade
```

### Deactivate venv

```bash
deactivate
```

---

## 🧪 Testing

### Test Backend Health

```bash
# In a new terminal (with venv activated)
curl http://localhost:5000/health
```

### Run Test Suite

```bash
source venv/bin/activate
python test_api.py
```

### Manual Test

```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What will Q4 demand look like?"}'
```

---

## 🔴 Running Backend (Different Methods)

### Method 1: Start Script (Recommended)

```bash
cd backend
./start.sh
```

### Method 2: Activate then Run

```bash
cd backend
source venv/bin/activate
python app.py
```

### Method 3: Direct Path

```bash
cd backend
./venv/bin/python app.py
```

### Method 4: Helper Script

```bash
cd backend
source activate.sh  # This activates venv
python app.py
```

---

## 🌐 Access Points

Once running, the backend is accessible at:

- **Main endpoint**: http://localhost:5000
- **Health check**: http://localhost:5000/health
- **Chat API**: http://localhost:5000/chat

---

## 📦 Package Management

### Add New Package

```bash
source venv/bin/activate
pip install package-name
pip freeze > requirements.txt
```

### Remove Package

```bash
source venv/bin/activate
pip uninstall package-name
pip freeze > requirements.txt
```

---

## 🐛 Troubleshooting

### venv not found

```bash
python3 -m venv venv
```

### Permission denied

```bash
chmod +x start.sh activate.sh
```

### Wrong Python version

```bash
deactivate
rm -rf venv
python3.9 -m venv venv  # Use specific version
source venv/bin/activate
pip install -r requirements.txt
```

### Port already in use

```bash
# Kill process on port 5000
lsof -ti:5000 | xargs kill -9
```

### ImportError after installing packages

```bash
# Make sure venv is activated
source venv/bin/activate
# Reinstall
pip install -r requirements.txt --force-reinstall
```

---

## ✅ Verify Setup

Run this to verify everything is working:

```bash
cd backend

# 1. Check venv exists
ls venv/bin/python
# Should show: venv/bin/python

# 2. Activate venv
source venv/bin/activate

# 3. Check Python path
which python
# Should show: .../backend/venv/bin/python

# 4. Check Flask installed
python -c "import flask; print(flask.__version__)"
# Should print version number

# 5. Check models exist
ls models/
# Should show .pkl files

# 6. Start server
python app.py
# Should start without errors
```

---

## 🔄 Daily Workflow

**Morning:**
```bash
cd backend
source venv/bin/activate
python app.py
```

**Working:**
- Make changes to `app.py`, `train.py`, etc.
- Server auto-reloads on file changes (debug mode)

**Testing:**
```bash
# New terminal
cd backend
source venv/bin/activate
python test_api.py
```

**End of day:**
```bash
# Ctrl+C to stop server
deactivate  # Exit venv
```

---

## 📝 Notes

- **Always activate venv** before running Python commands
- The `venv/` folder is excluded from git (in `.gitignore`)
- The venv is platform-specific, recreate on different machines
- Use `pip freeze > requirements.txt` to save new dependencies

---

## 🚀 Production Deployment

For production, use a WSGI server instead of Flask's development server:

```bash
source venv/bin/activate
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

---

Built for **NextGenHackathon 2025** 🎯
