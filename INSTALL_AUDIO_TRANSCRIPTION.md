# 🎙️ Installing Real Audio Transcription (Faster Whisper)

## Current Issue

You're seeing:
```
[MOCK] This is a test transcription. Faster Whisper is not installed.
```

This is because the **faster-whisper** package isn't installed yet.

---

## ✅ Quick Install (Easy Method)

### **Step 1: Install faster-whisper**

Open your backend terminal and run:

```bash
cd backend
venv\Scripts\activate
pip install faster-whisper
```

This will install the Python package. **That's it!**

### **Step 2: Restart Backend**

Stop the server (Ctrl+C) and restart:

```bash
python -m src.main
```

### **Step 3: Test**

Now try recording audio in your extension. It should transcribe real audio!

---

## 📋 What Gets Installed

When you run `pip install faster-whisper`, it installs:

- **faster-whisper** - The transcription library
- **Dependencies** - All required packages
- **Whisper models** - Downloaded automatically on first use

The first time you use audio transcription, it will download the **base** model (~150MB).

---

## ⚙️ Configuration

Your `.env` file already has the right settings:

```env
WHISPER_MODEL=base           # Model size (base is recommended)
WHISPER_DEVICE=cpu           # Use CPU (or 'cuda' for GPU)
WHISPER_COMPUTE_TYPE=int8    # Optimized for CPU
```

### Available Models

| Model | Size | Speed | Accuracy | Recommended For |
|-------|------|-------|----------|-----------------|
| **tiny** | ~75MB | Very Fast | Lower | Quick testing |
| **base** | ~150MB | Fast | Good | **Recommended** ✅ |
| **small** | ~500MB | Medium | Better | High accuracy needed |
| **medium** | ~1.5GB | Slow | High | Professional use |
| **large** | ~3GB | Very Slow | Best | Maximum accuracy |

**For your use case, `base` is perfect!**

---

## 🔧 Advanced: Install with GPU Support (Optional)

If you have an NVIDIA GPU and want faster transcription:

### **Step 1: Install CUDA Toolkit**

Download from: https://developer.nvidia.com/cuda-downloads

### **Step 2: Install GPU-enabled version**

```bash
pip install faster-whisper[cuda]
```

### **Step 3: Update .env**

```env
WHISPER_DEVICE=cuda
WHISPER_COMPUTE_TYPE=float16
```

---

## 🐛 Troubleshooting

### Issue 1: "ModuleNotFoundError: No module named 'faster_whisper'"

**Solution:**
```bash
cd backend
venv\Scripts\activate
pip install faster-whisper
```

### Issue 2: First transcription is slow

**This is normal!** The first time you use it:
- Downloads the model (~150MB for base)
- Takes 30-60 seconds
- After that, it's fast!

### Issue 3: "ffmpeg not found"

Faster Whisper needs ffmpeg. Install it:

**Windows (using Chocolatey):**
```bash
choco install ffmpeg
```

**Or download manually:**
1. Go to: https://ffmpeg.org/download.html
2. Download Windows build
3. Extract to `C:\ffmpeg`
4. Add to PATH: `C:\ffmpeg\bin`

**Verify installation:**
```bash
ffmpeg -version
```

### Issue 4: Still seeing MOCK transcription

**Check:**
1. Did you install faster-whisper?
   ```bash
   pip list | findstr faster-whisper
   ```

2. Did you restart the backend?

3. Check backend logs for errors

---

## ✅ Verification

After installing, your backend logs should show:

```
[info] Initializing Faster Whisper model=base device=cpu compute_type=int8
[info] Faster Whisper model loaded successfully
```

If you see:
```
[warning] Faster Whisper not available - using mock mode for testing
```

Then faster-whisper is **not installed correctly**.

---

## 🎯 Complete Installation Commands

**Just run these in order:**

```bash
# 1. Navigate to backend
cd backend

# 2. Activate virtual environment
venv\Scripts\activate

# 3. Install faster-whisper
pip install faster-whisper

# 4. Verify installation
pip list | findstr faster-whisper

# 5. Restart backend
python -m src.main
```

**That's it! Audio transcription will now work!** 🎉

---

## 📊 Expected Behavior

**After installation:**

1. **First audio recording:**
   - Downloads model (~30-60 seconds)
   - Shows progress in logs
   - Saves model for future use

2. **Subsequent recordings:**
   - Instant transcription
   - No downloads needed
   - Fast and accurate

**Transcription quality:**
- **Excellent** for clear English speech
- **Good** for accented English
- **Multi-language** support (99 languages)
- **Real-time** capable

---

## 💡 Tips for Best Results

1. **Speak clearly** into the microphone
2. **Minimize background noise**
3. **Record at least 1-2 seconds** of audio
4. **Use a good microphone** if possible
5. **English works best** (trained on English data)

---

## 🔄 Switching Models

To use a different model, edit `backend\.env`:

**For faster (but less accurate):**
```env
WHISPER_MODEL=tiny
```

**For better accuracy (but slower):**
```env
WHISPER_MODEL=small
```

Then restart the backend.

---

**Ready to install? Run the commands above!** 🚀
