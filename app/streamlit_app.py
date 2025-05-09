import streamlit as st
import requests

# Get the bearer token from the URL
auth_token = st.query_params.get("auth")

st.set_page_config(page_title="OAuth2 OBO Demo", layout="centered")

if not auth_token:
    st.title("🔒 Login Required")
    login_url = "http://localhost:3500/v1.0/invoke/streamlit-wrapper/method/auth"
    st.markdown(
        f'<a href="{login_url}" target="_self">'
        f'<button style="font-size:24px;padding:10px 20px;">Login with Microsoft</button>'
        f'</a>',
        unsafe_allow_html=True
    )
else:
    st.title("Logged In")

    st.subheader("Original Token")
    st.code(auth_token)

    if "obo_token" not in st.session_state:
        st.session_state.obo_token = None

    if st.button("Exchange Token"):
        with st.spinner("Exchanging token via OBO..."):
            try:
                response = requests.get(
                    "http://localhost:8000/exchange",
                    headers={"Authorization": f"Bearer {auth_token}"}
                )
                if response.status_code == 200:
                    obo_token = response.json().get("obo_access_token")
                    st.session_state.obo_token = obo_token
                else:
                    st.error(f"Token exchange failed: {response.json()}")
            except Exception as e:
                st.error(f"Error during token exchange: {e}")

    if st.session_state.obo_token:
        st.subheader("OBO Access Token")
        st.code(st.session_state.obo_token)