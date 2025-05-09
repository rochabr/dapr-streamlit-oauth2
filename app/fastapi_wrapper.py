from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, JSONResponse
import subprocess
import requests
import msal
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# MSAL OBO Configuration
CLIENT_ID = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]
TENANT_ID = os.environ["TENANT_ID"]
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
DOWNSTREAM_API_SCOPE = os.environ["API_SCOPE"]

@app.get("/auth")
async def auth(request: Request):
    print("Incoming request headers:")
    for k, v in request.headers.items():
        print(f"  {k}: {v}")

    auth_header = request.headers.get("authorization")
    if auth_header:
        print("Authorization header received.")
    else:
        print("No Authorization header received.")

    # Redirect to Streamlit frontend with auth token in query string
    return RedirectResponse(f"http://localhost:8501/?auth={auth_header or ''}")


@app.get("/exchange")
async def exchange_token(request: Request):
    original_token = request.headers.get("authorization", "").replace("Bearer ", "")

    if not original_token:
        return JSONResponse(status_code=400, content={"error": "Missing bearer token"})

    app_msal = msal.ConfidentialClientApplication(
        client_id=CLIENT_ID,
        client_credential=CLIENT_SECRET,
        authority=AUTHORITY,
    )

    result = app_msal.acquire_token_on_behalf_of(
        user_assertion=original_token,
        scopes=[DOWNSTREAM_API_SCOPE],
    )

    if "access_token" in result:
        # Optional: Call a protected downstream API (not implemented yet)
        # downstream_response = requests.get(
        #     "http://localhost:8000/protected-resource",
        #     headers={"Authorization": f"Bearer {result['access_token']}"}
        # )
        # return {"downstream_result": downstream_response.json()}

        return {"obo_access_token": result["access_token"]}
    else:
        return JSONResponse(
            status_code=500,
            content={"error": result.get("error_description", "Token exchange failed")}
        )


# Launch Streamlit in background if not already running
subprocess.Popen(["streamlit", "run", "app/streamlit_app.py"])