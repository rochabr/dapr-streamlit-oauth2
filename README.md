# Streamlit + Dapr OAuth2 Login + On-Behalf-Of Flow Demo

This project demonstrates an OAuth2 login flow using [Dapr's HTTP middleware](https://docs.dapr.io/reference/components/middleware/http/middleware-oauth2/) with a `Streamlit` frontend, a `FastAPI` proxy, and a secure [On-Behalf-Of (OBO) token exchange](https://learn.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-on-behalf-of-flow) using Microsoft Entra ID (Azure AD).

---

## Components

- **Streamlit UI**: User-facing app that initiates login and displays tokens.
- **FastAPI Gateway**: Acts as a proxy for Dapr's redirect and handles token exchange.
- **Dapr OAuth2 Middleware**: Handles user authentication.
- **MSAL**: Performs OBO token exchange using Azure-issued tokens.

---

## Features

✅ OAuth2 Authorization Code Flow via Dapr  
✅ Dapr OAuth2 Middleware Integration  
✅ PKCE Flow Redirection from Streamlit  
✅ On-Behalf-Of Token Exchange with Azure  
✅ `.env`-based Secret Injection

---

## Prerequisites

- Python 3.10+
- [Dapr CLI](https://docs.dapr.io/get-dapr/cli/)
- Azure Entra ID Tenant
- 2 App Registrations in Azure:
  - Frontend (Streamlit App)
  - Backend (API with `access_as_user` scope)

---

## 📁 Project Structure

```
.
├── app/
│   ├── streamlit_app.py          # Streamlit UI with login + exchange buttons
│   └── fastapi_wrapper.py        # FastAPI wrapper for Dapr and OBO endpoint
├── components/
│   └── oauth2.yaml               # Dapr OAuth2 middleware component (auto-generated)
├── config/
│   └── oauth2-config.yaml        # Dapr HTTP middleware pipeline config
├── render_oauth2.py              # Script to render oauth2.yaml from .env
├── .env                          # Your environment secrets (not committed)
├── .env.example                  # Template for environment variables
├── README.md
```

---

## ⚙Setup

### 1. Clone and install dependencies

```bash
git clone https://github.com/your-org/dapr-obo-demo.git
cd dapr-obo-demo
pip install -r requirements.txt
```

### 2. Configure environment

Copy the example and fill in your Azure credentials:

```bash
cp .env.example .env
```

Edit `.env` with:
- Your tenant ID
- Azure app registration values
- API scopes

### 3. Update the component file

Update `oauth2.yaml` with your application IDs, client secrets, tenant IDs, and scopes.

### 4. Run the app

```bash
dapr run   --app-id streamlit-wrapper   --app-port 8000   --dapr-http-port 3500   --config ./config/oauth2-config.yaml   --resources-path ./components   --log-level debug   -- uvicorn app.fastapi_wrapper:app --host 0.0.0.0 --port 8000
```

Then open [http://localhost:8501](http://localhost:8501) in your browser.

---

## How It Works

1. Streamlit shows a **Login with Microsoft** button.
2. Clicking it sends user to `http://localhost:3500/v1.0/invoke/streamlit-wrapper/method/auth` (handled by FastAPI).
3. Dapr OAuth2 middleware redirects user to Azure login.
4. Azure redirects back to FastAPI → which then sends user to Streamlit with a bearer token.
5. Streamlit displays the token and allows the user to **Exchange Token** via `/exchange`, using MSAL's OBO flow.
6. The access token is exchanged for one with `access_as_user` scope targeting a downstream API.

---

## `.env.example`

```env
# Azure AD Tenant ID
TENANT_ID=your-tenant-id-here

# Client App (frontend) registration
CLIENT_ID=your-frontend-client-id
CLIENT_SECRET=your-frontend-client-secret

# Backend API App registration
API_CLIENT_ID=your-backend-api-client-id
API_SCOPE=api://your-backend-api-client-id/access_as_user

# Frontend App scope (must match exposed scope from frontend app registration)
FRONTEND_SCOPE=api://your-frontend-client-id/user_impersonation

# OAuth2 endpoints (derived from your tenant ID)
AUTH_URL=https://login.microsoftonline.com/${TENANT_ID}/oauth2/v2.0/authorize
TOKEN_URL=https://login.microsoftonline.com/${TENANT_ID}/oauth2/v2.0/token

# Dapr redirect URL (must match what's configured in Azure app registration)
REDIRECT_URL=http://localhost:3500/v1.0/invoke/streamlit-wrapper/method/auth
```

---

## Security Notes

- Tokens are stored in memory/session only.
- Use HTTPS in production.
- Do not commit your `.env` file.
- Use Azure Key Vault and Dapr secrets API for production-grade credential management.

---

## Azure AD App Registrations

This demo requires **two applications registered in Azure Entra ID (formerly Azure AD)**.

### 1. Register the Frontend App (`streamlit-dapr-demo`)

This app represents the Streamlit frontend that initiates OAuth2 login.

1. Go to [Azure Portal > App registrations](https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps)
2. Click **"New registration"**
3. Name: `streamlit-dapr-demo`
4. Supported account types: **Single tenant**
5. Redirect URI: `http://localhost:3500/v1.0/invoke/streamlit-wrapper/method/auth`
6. Click **Register**
7. Go to **Expose an API**:
   - Click **"Set"** Application ID URI → accept default or use: `api://<client-id>`
   - Add a scope:
     - Name: `user_impersonation`
     - Admin consent display name: `Access streamlit-dapr-demo`
     - Admin consent description: `Allow access to streamlit-dapr-demo`
8. Go to **Certificates & secrets** → **New client secret** and copy the value

### 2. Register the Backend App (`streamlit-dapr-demo-api`)

This app represents the downstream API that will receive OBO tokens.

1. Go to **App registrations** → **New registration**
2. Name: `streamlit-dapr-demo-api`
3. Supported account types: **Single tenant**
4. Click **Register**
5. Go to **Expose an API**:
   - Set Application ID URI (e.g., `api://<backend-client-id>`)
   - Add a scope:
     - Name: `access_as_user`
     - Admin consent name: `Access demo API`
     - Admin consent description: `Allow this API to be accessed via OBO flow`
6. Go to **API permissions** for `streamlit-dapr-demo`
   - Add a permission → **My APIs** → select `streamlit-dapr-demo-api`
   - Choose **Delegated permissions** → check `access_as_user`
   - Click **Grant admin consent**

After this setup, the `streamlit-dapr-demo` frontend can acquire a user token and use it in an OBO flow to call `streamlit-dapr-demo-api`.
