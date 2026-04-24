# Azure OpenAI Deployment Setup Guide

**Goal:** Create a deployment named `gpt-5.4-nano` in your Azure OpenAI resource

**Current Status:**
- ✅ `.env` configured for `gpt-5.4-nano`
- ❌ Azure Portal doesn't have this deployment yet
- ⚠️ Getting 401 error because deployment doesn't exist

---

## Step-by-Step Instructions

### Step 1: Log into Azure Portal

1. Go to: https://portal.azure.com
2. Sign in with your Azure account
3. Search for your OpenAI resource: **ftaks-meizyzig-eastus2**

---

### Step 2: Navigate to Deployments

1. Click on your OpenAI resource
2. In the left sidebar, find **"Model deployments"** or **"Deployments"**
3. Click on it

---

### Step 3: Check Current Deployments

You should see a list of existing deployments. Check if you have:
- `gpt-4o` (likely exists)
- `gpt-4` 
- `gpt-35-turbo`
- Others...

**Take note of what models you have available.**

---

### Step 4: Create New Deployment

#### Option A: If GPT-5.4-nano Model is Available

1. Click **"+ Create new deployment"** or **"+ Deploy model"**
2. **Select model:** 
   - Look for `gpt-5.4-nano` in the dropdown
   - If not available, see Option B below
3. **Deployment name:** `gpt-5.4-nano` (MUST match exactly)
4. **Model version:** Latest or Auto-update
5. **Deployment type:** Standard
6. **Tokens per Minute Rate Limit:** 10K (or your preference)
7. Click **"Create"** or **"Deploy"**
8. Wait 1-2 minutes for deployment to complete

#### Option B: If GPT-5.4-nano is NOT Available

**Important:** Azure may not have a model called "GPT-5.4-nano". This might be:
- A future model that doesn't exist yet
- A custom name you wanted to use
- A typo for a different model

**Solution:** Create deployment with an available model

1. Click **"+ Create new deployment"**
2. **Select model:** Choose what's available:
   - **Recommended:** `gpt-4o` (most capable, supports vision)
   - Alternative: `gpt-4-turbo`
   - Alternative: `gpt-4`
3. **Deployment name:** `gpt-5.4-nano` (even though model is different)
4. This way your code will work without changes
5. Deploy

**Example:**
```
Model: gpt-4o
Deployment Name: gpt-5.4-nano
```

This creates a deployment that your code can access via the name `gpt-5.4-nano`.

---

### Step 5: Verify Deployment

After creation:

1. You should see the deployment in the list
2. Status should be **"Succeeded"** or **"Running"**
3. Note the **endpoint URL** (should match your .env)
4. Note the **API key** (should match your .env)

---

### Step 6: Test with Azure CLI (Optional)

If you have Azure CLI installed:

```bash
# List all deployments
az cognitiveservices account deployment list \
  --resource-group <your-resource-group> \
  --name ftaks-meizyzig-eastus2

# Should show your new deployment: gpt-5.4-nano
```

---

## Current Configuration Check

Your `.env` file has:
```env
AZURE_OPENAI_API_KEY=4lYNYfD0QSw3F6EqOBziBsVlwRRRZ3HbnjOePrSsNekqxI6RmHaqJQQJ99BHACHYHv6XJ3w3AAAAACOGa9ULcontinues
AZURE_OPENAI_ENDPOINT=https://ftaks-meizyzig-eastus2.cognitiveservices.azure.com
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-5.4-nano
```

After you create the deployment, these should all match:
- ✅ Endpoint matches your Azure resource
- ✅ API key is valid
- ✅ Deployment name exists: `gpt-5.4-nano`

---

## Testing After Setup

### Test 1: Restart Backend

```bash
# Stop current backend (Ctrl+C in terminal or)
pkill -f "python -m src.main"

# Start fresh
cd "D:\All_project\JAI SHREE RAM\lockedin-ai\backend"
python -m src.main
```

### Test 2: Health Check

```bash
curl http://localhost:8000/api/v1/health
```

**Expected output:**
```json
{
    "status": "healthy",
    "version": "1.0.0",
    "services": {
        "openai": "healthy",
        "audio": "unhealthy"
    }
}
```

Note: Audio will still be "unhealthy" (that's ok - it's in mock mode).

### Test 3: Chat Completion

```bash
curl -X POST http://localhost:8000/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-API-Key: MySecretKey12345!@#$%" \
  -d '{
    "messages": [
      {"role": "user", "content": "Say hello in one word"}
    ],
    "max_tokens": 10
  }'
```

**Expected output:**
```json
{
    "content": "Hello!",
    "session_id": null,
    "context_used": 1,
    "created_at": "2026-04-22T..."
}
```

---

## Troubleshooting

### Still Getting 401 Error?

**Check:**
1. Deployment name is EXACTLY `gpt-5.4-nano` (case-sensitive)
2. Deployment status is "Succeeded" in Azure Portal
3. API key in `.env` matches Azure Portal key
4. Endpoint URL in `.env` matches Azure Portal endpoint
5. Deployment is in same region as endpoint

### Getting 404 Error?

**Fix:**
- Deployment name doesn't match
- Go to Azure Portal and rename deployment to `gpt-5.4-nano`

### Getting Rate Limit Error?

**Fix:**
- Increase TPM (Tokens Per Minute) in deployment settings
- Or reduce request frequency

---

## Quick Reference

### Azure Portal Navigation
```
Azure Portal
  → Search: "ftaks-meizyzig-eastus2"
    → Your OpenAI Resource
      → Left Menu: "Model deployments"
        → Create new deployment
          → Model: (select available model)
          → Name: gpt-5.4-nano
          → Deploy
```

### Expected Timeline
- Deployment creation: 1-2 minutes
- Testing backend: 1 minute
- Total: **5 minutes**

---

## After Azure Setup is Complete

Come back and run:
```bash
# In the project root
bash test_api.sh
```

This will test all endpoints and show you if everything is working!

---

**Need Help?**

If deployment creation fails:
1. Check you have available quota
2. Check model availability in your region (eastus2)
3. Try a different model (gpt-4o is most reliable)
4. Check Azure status page for outages

**Ready to proceed?** Follow the steps above, then come back to test! 🚀
