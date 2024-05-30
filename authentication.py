import streamlit as st
import os
import re
import jwt
import datetime

SECRET_KEY = os.environ.get('SECRET_KEY')



def check_authentication(password):
    return password == os.getenv('PASSWORD')

def authenticate():
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
    expiration = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=15)
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

def authenticate_user(email, password, supabase, controller):
    try:
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        if response.user:
            user_email = response.user.email  # Accessing user email correctly
            token = generate_jwt(user_email)
            expiration_date = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=15)
            controller.set('prd_prateek', token,"/",expiration_date)
            st.session_state['logged_in'] = True
            st.session_state['user'] = response.user
            st.success(f"Welcome {user_email}")
            st.rerun()
        else:
            st.error("Authentication failed. Please check your email and password.")
    except Exception as e:
        st.error(f"Authentication failed: {e}")

def send_reset_password_email(email, supabase):
    try:
        supabase.auth.api.reset_password_for_email(email)
        st.success("Password reset email sent. Please check your inbox.")
    except Exception as e:
        st.error(f"Failed to send password reset email: {e}")

def register_user(email, password, supabase):
    try:
        response = supabase.auth.sign_up({"email": email, "password": password})
        if response.user:
            st.success("Registration successful. Email confirmation email sent. COnfirm your email & then login.")
        else:
            st.error("Registration failed. Please try again.")
    except Exception as e:
        st.error(f"Registration failed: {e}")


def auth_screen(supabase, controller):

    if controller.get('prd_prateek'):
        token = controller.get('prd_prateek')
        user_data = verify_jwt(token)
        if user_data:
            st.session_state['logged_in'] = True
            st.session_state['user'] = {"email": user_data["email"]}
        else:
            st.session_state['logged_in'] = False
            controller.remove('prd_prateek')

    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if st.session_state['logged_in']:
        st.sidebar.success(f"Welcome {st.session_state['user']['email']}")
        if st.sidebar.button("Logout"):
            st.session_state['logged_in'] = False
            st.session_state.pop('user', None)
            controller.remove('prd_prateek')
            res = supabase.auth.sign_out()
            st.rerun()
    else:
        auth_mode = st.radio("Select mode", ["Login", "Register"])
        st.markdown(f'## <div>{"Welcome back!" if auth_mode == "Login" else "Create an account"}</div>', unsafe_allow_html=True)
        
        email = st.text_input("Email", key="email", label_visibility="collapsed", placeholder="Email", help="Enter your email address")
        password = st.text_input("Password", key="password", label_visibility="collapsed", placeholder="Password", type="password", help="Enter your password")
        
        if auth_mode == "Login":
            if st.button("Log In", key="login"):
                if is_valid_email(email):
                    authenticate_user(email, password, supabase, controller)
                else:
                    st.error("Please enter a valid email address")
            if st.button("Forgot Password?", key="forgot_password"):
                if is_valid_email(email):
                    send_reset_password_email(email, supabase)
                else:
                    st.error("Please enter a valid email address")
        
        elif auth_mode == "Register":
            if st.button("Register", key="register"):
                if is_valid_email(email):
                    register_user(email, password, supabase)
                else:
                    st.error("Please enter a valid email address")

        elif auth_mode == "Reset Password":
            if st.button("Reset Password", key="reset_password"):
                if is_valid_email(email):
                    send_reset_password_email(email, supabase)
                else:
                    st.error("Please enter a valid email address")