import streamlit as st
import os
import re
import jwt
import datetime
from streamlit_cookies_manager import EncryptedCookieManager

SECRET_KEY = os.environ.get('SECRET_KEY')
def check_authentication(password):
    return password == os.getenv('PASSWORD')

def authenticate_user():
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False

    # Create a placeholder for the login form
    login_placeholder = st.empty()

    if not st.session_state['authenticated']:
        with login_placeholder.container():
            pwd_input = st.text_input("Password:", type="password", key="pwd")
            if st.button("Login", key="login_button"):
                st.session_state['authenticated'] = check_authentication(pwd_input)
                if st.session_state['authenticated']:
                    # Clear the login placeholder if authenticated
                    login_placeholder.empty()
                else:
                    st.error("Incorrect password, please try again.")


def is_valid_email(email):
    """Validate the email format."""
    regex = r'^\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.match(regex, email)

def generate_jwt(user_email):
    expiration = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1)
    token = jwt.encode({"email": user_email, "exp": expiration}, SECRET_KEY, algorithm="HS256")
    return token

def verify_jwt(token):
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return decoded_token
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def authenticate_user(email, password,supabase,cookies):
    try:
        response = supabase.auth.sign_in(email=email, password=password)
        if response.get('user'):
            token = generate_jwt(response['user']['email'])
            cookies.set("auth_token", token, expires_at=datetime.datetime.utcnow() + datetime.timedelta(days=1))
            st.session_state['logged_in'] = True
            st.session_state['user'] = response['user']
            st.success(f"Welcome {response['user']['email']}")
        else:
            st.error("Authentication failed. Please check your email and password.")
    except Exception as e:
        st.error(f"Authentication failed: {e}")

def send_reset_password_email(email,supabase):
    try:
        supabase.auth.api.reset_password_for_email(email)
        st.success("Password reset email sent. Please check your inbox.")
    except Exception as e:
        st.error(f"Failed to send password reset email: {e}")

def register_user(email, password,supabase):
    try:
        response = supabase.auth.sign_up(email=email, password=password)
        if response.get('user'):
            st.success("Registration successful. Please check your email to confirm your account.")
        else:
            st.error("Registration failed. Please try again.")
    except Exception as e:
        st.error(f"Registration failed: {e}")

def auth_screen(supabase):
    cookies = EncryptedCookieManager(
        prefix="myapp_",  # prefix for cookie names to avoid collision
        password="password",  # password for cookie encryption
    )
    if not cookies.ready():
        st.stop()

    st.set_page_config(page_title="Login", page_icon="🔒")

    st.markdown("""
    <style>
    .main {
        background-color: #5865F2;
        padding-top: 50px;
        padding-bottom: 50px;
    }
    .login-container {
        background-color: #2C2F33;
        padding: 50px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        width: 100%;
        max-width: 400px;
        margin: auto;
    }
    .login-title {
        font-size: 24px;
        color: #FFFFFF;
        text-align: center;
        margin-bottom: 20px;
    }
    .login-subtitle {
        font-size: 14px;
        color: #99AAB5;
        text-align: center;
        margin-bottom: 20px;
    }
    .login-label {
        font-size: 14px;
        color: #99AAB5;
        margin-bottom: 10px;
    }
    .login-input {
        background-color: #23272A;
        color: #FFFFFF;
        border: none;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 20px;
        width: 100%;
    }
    .login-button {
        background-color: #7289DA;
        color: #FFFFFF;
        padding: 10px;
        border: none;
        border-radius: 5px;
        width: 100%;
        cursor: pointer;
        font-size: 16px;
    }
    .forgot-password, .register {
        font-size: 12px;
        color: #99AAB5;
        text-decoration: none;
    }
    </style>
    """, unsafe_allow_html=True)

    if "auth_token" in cookies:
        token = cookies.get("auth_token")
        user_data = verify_jwt(token)
        if user_data:
            st.session_state['logged_in'] = True
            st.session_state['user'] = {"email": user_data["email"]}
        else:
            st.session_state['logged_in'] = False
            cookies.delete("auth_token")

    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if st.session_state['logged_in']:
        st.success(f"Welcome {st.session_state['user']['email']}")
        if st.button("Logout"):
            st.session_state['logged_in'] = False
            st.session_state.pop('user', None)
            cookies.delete("auth_token")
            st.experimental_rerun()
    else:
        auth_mode = st.radio("Select mode", ["Login", "Register", "Reset Password"])

        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown(f'<div class="login-title">{"Welcome back!" if auth_mode == "Login" else "Create an account"}</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-subtitle">We\'re so excited to see you again!</div>', unsafe_allow_html=True)
        
        email = st.text_input("Email", key="email", label_visibility="collapsed", placeholder="Email", help="Enter your email address")
        password = st.text_input("Password", key="password", label_visibility="collapsed", placeholder="Password", type="password", help="Enter your password")
        
        if auth_mode == "Login":
            col1, col2 = st.columns([1, 3])
            with col1:
                if st.button("Forgot Password?", key="forgot_password"):
                    if is_valid_email(email):
                        send_reset_password_email(email,supabase)
                    else:
                        st.error("Please enter a valid email address")
            with col2:
                st.markdown('<a href="#" class="register">Need an account? Register</a>', unsafe_allow_html=True)

            if st.button("Log In", key="login"):
                if is_valid_email(email):
                    authenticate_user(email, password,supabase,cookies)
                else:
                    st.error("Please enter a valid email address")
        
        elif auth_mode == "Register":
            if st.button("Register", key="register"):
                if is_valid_email(email):
                    register_user(email, password,supabase)
                else:
                    st.error("Please enter a valid email address")

        elif auth_mode == "Reset Password":
            if st.button("Reset Password", key="reset_password"):
                if is_valid_email(email):
                    send_reset_password_email(email,supabase)
                else:
                    st.error("Please enter a valid email address")

        st.markdown('</div>', unsafe_allow_html=True)