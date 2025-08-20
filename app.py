import streamlit as st
import requests

# -------------------------
# Configuration
# -------------------------
API_URL = "https://aipropiq.com/wp-json/wsp-route/v1/wsp-view-subscription"
ADMIN_USERS = ["admin", "superadmin"]  # 👈 whitelist of WordPress admins

def check_subscription(username: str, consumer_secret: str):
    """
    Check if user has an active subscription OR is admin.
    """
    try:
        response = requests.get(API_URL, params={"consumer_secret": consumer_secret}, timeout=10)
        if response.status_code != 200:
            return False, f"API error: {response.text}"
        
        data = response.json()
        if data.get("status") != "success":
            return False, "Invalid API response"
        
        subscriptions = data.get("data", [])
        
        # --- Admins have full access ---
        if username in ADMIN_USERS:
            return True, {"role": "admin", "msg": "Admin access granted"}
        
        # --- Check if subscription active ---
        for sub in subscriptions:
            if sub.get("user_name") == username and sub.get("status") == "active":
                return True, {"role": "subscriber", **sub}
        
        return False, "No active subscription found"
    
    except Exception as e:
        return False, str(e)

def main():
    st.title("🔐 WooCommerce Subscription Login")
    
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.user = None
        st.session_state.subscription = None
        st.session_state.role = None
    
    if not st.session_state.authenticated:
        with st.form("login_form"):
            username = st.text_input("WordPress Username")
            consumer_secret = st.text_input("Consumer Secret", type="password")
            submit = st.form_submit_button("Login")
        
        if submit:
            with st.spinner("Validating access..."):
                valid, result = check_subscription(username, consumer_secret)
                
                if valid:
                    st.session_state.authenticated = True
                    st.session_state.user = username
                    st.session_state.subscription = result
                    st.session_state.role = result.get("role", "subscriber")
                    
                    if st.session_state.role == "admin":
                        st.success(f"✅ Welcome {username} (Admin)")
                    else:
                        st.success(f"✅ Welcome {username}, subscription active!")
                else:
                    st.error(f"❌ Access denied: {result}")
    
    else:
        st.success(f"Logged in as {st.session_state.user} ({st.session_state.role})")
        
        if st.session_state.role == "subscriber":
            st.write("### Subscription details")
            st.json(st.session_state.subscription)
        elif st.session_state.role == "admin":
            st.info("🔑 Full Admin Access Granted")
        
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.session_state.subscription = None
            st.session_state.role = None

if __name__ == "__main__":
    main()
