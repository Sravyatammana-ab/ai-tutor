# Fix Azure Document Intelligence Configuration Error

## Problem
Getting error: "Azure Document Intelligence service is not available. Please configure AZURE_ENDPOINT and AZURE_KEY"

## Root Cause
The environment variables are not being read correctly on Render, even though they're set.

## Solution Steps

### Step 1: Verify Environment Variables in Render Dashboard

1. Go to **Render Dashboard**: https://dashboard.render.com
2. Click on your backend service (`ai-tutor-bknj`)
3. Go to **Environment** tab
4. Verify these variables exist **exactly** (case-sensitive):

```
AZURE_ENDPOINT=https://ai-tutor-document-intelligence.cognitiveservices.azure.com/
AZURE_KEY=your-azure-key-here
```

**Important Checks:**
- ✅ No quotes around values (Render adds them automatically if needed)
- ✅ No extra spaces before/after the `=` sign
- ✅ Variable names are **exactly** `AZURE_ENDPOINT` and `AZURE_KEY` (uppercase)
- ✅ Values match what you have in your `.env` file

### Step 2: Restart Render Service

After verifying/updating environment variables:

1. In Render Dashboard → Your Service
2. Click **Manual Deploy** → **Clear build cache & deploy**
3. OR click **Restart** button
4. Wait for deployment to complete (3-5 minutes)

### Step 3: Test Configuration

After deployment, test the debug endpoint:

```bash
curl https://ai-tutor-bknj.onrender.com/api/debug/config
```

Expected response:
```json
{
  "azure_endpoint_set": true,
  "azure_endpoint_preview": "https://ai-tutor-document-intelligence.cognitiveservices.azure.com/...",
  "azure_key_set": true,
  "azure_key_length": 64,
  "env_azure_endpoint": true,
  "env_azure_key": true
}
```

If any value is `false`, the environment variable is not set correctly.

### Step 4: Check Render Logs

1. Go to Render Dashboard → Your Service → **Logs** tab
2. Look for these messages:
   - ✅ `"✓ Azure Document Intelligence service initialized successfully"` = Working!
   - ❌ `"ERROR: Azure configuration missing"` = Variables not set
   - ❌ `"ERROR: Azure Document Intelligence service initialization failed"` = Check endpoint/key

### Step 5: Common Issues & Fixes

#### Issue 1: Variables Not Showing in Debug Endpoint

**Fix:**
- Delete the environment variable in Render
- Re-add it with the exact name and value
- Restart the service

#### Issue 2: Trailing Slash

Your endpoint has a trailing slash: `https://...azure.com/`

**This is OK** - the code automatically removes it. But if you want to be safe:
- Remove the trailing slash in Render: `https://ai-tutor-document-intelligence.cognitiveservices.azure.com`

#### Issue 3: Wrong Variable Names

Make sure you're using:
- `AZURE_ENDPOINT` (not `AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT`)
- `AZURE_KEY` (not `AZURE_API_KEY` or `AZURE_DOCUMENT_INTELLIGENCE_KEY`)

#### Issue 4: Service Not Restarted

**After adding/updating environment variables, you MUST restart the service!**

### Step 6: Verify Azure Service is Accessible

Test if your Azure endpoint is reachable:

```bash
curl -X POST "https://ai-tutor-document-intelligence.cognitiveservices.azure.com/formrecognizer/documentModels/prebuilt-read:analyze?api-version=2023-10-31" \
  -H "Ocp-Apim-Subscription-Key: YOUR_AZURE_KEY_HERE" \
  -H "Content-Type: application/json" \
  -d '{}'
```

If this returns an error, check:
- Azure portal → Your Document Intelligence resource → Keys & Endpoint
- Verify the endpoint URL matches
- Verify the key is correct

---

## Quick Checklist

- [ ] Environment variables set in Render Dashboard (not just `.env` file)
- [ ] Variable names are exact: `AZURE_ENDPOINT` and `AZURE_KEY`
- [ ] No extra spaces or quotes in values
- [ ] Service restarted after adding variables
- [ ] Debug endpoint shows `azure_endpoint_set: true` and `azure_key_set: true`
- [ ] Render logs show successful initialization

---

## After Fixing

Once fixed, try uploading a document again. The error should be gone!

If you still get errors, check the Render logs for the specific error message from Azure.

