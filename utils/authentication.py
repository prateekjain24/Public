import streamlit as st
import os
import re
import jwt
from datetime import datetime, timedelta

SECRET_KEY = os.environ.get('SECRET_KEY')

def is_valid_email(email):
    """Validate the email format."""
    regex = r'^\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.match(regex, email)

def generate_jwt(user_email):
    expiration = datetime.utcnow() + timedelta(days=30)  # Token expires in 30 days
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

def set_auth_cookie(token):
    st.session_state.auth_token = token
    js_code = f"""
    <script>
    function setCookie(name, value, days) {{
        var expires = "";
        if (days) {{
            var date = new Date();
            date.setTime(date.getTime() + (days*24*60*60*1000));
            expires = "; expires=" + date.toUTCString();
        }}
        document.cookie = name + "=" + (value || "")  + expires + "; path=/";
    }}
    setCookie('auth_token', '{token}', 30);
    </script>
    """
    st.components.v1.html(js_code, height=0)

def get_auth_cookie():
    if 'auth_token' not in st.session_state:
        js_code = """
        <script>
        function getCookie(name) {
            var nameEQ = name + "=";
            var ca = document.cookie.split(';');
            for(var i=0;i < ca.length;i++) {
                var c = ca[i];
                while (c.charAt(0)==' ') c = c.substring(1,c.length);
                if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
            }
            return null;
        }
        var auth_token = getCookie('auth_token');
        if (auth_token) {
            window.parent.postMessage({type: 'SET_COOKIE', cookie: auth_token}, '*');
        }
        </script>
        """
        st.components.v1.html(js_code, height=0)
        
        # JavaScript to send the cookie value to session state
        st.components.v1.html(
            """
            <script>
            window.addEventListener('message', function(event) {
                if (event.data.type === 'SET_COOKIE') {
                    window.parent.Streamlit.setComponentValue(event.data.cookie);
                }
            }, false);
            </script>
            """,
            height=0
        )
    
    return st.session_state.get('auth_token')

def clear_auth_cookie():
    if 'auth_token' in st.session_state:
        del st.session_state.auth_token
    js_code = """
    <script>
    function deleteCookie(name) {
        document.cookie = name +'=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;';
    }
    deleteCookie('auth_token');
    </script>
    """
    st.components.v1.html(js_code, height=0)

def authenticate_user(email, password, supabase):
    try:
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        if response.user:
            user_email = response.user.email
            token = generate_jwt(user_email)
            set_auth_cookie(token)
            st.session_state['logged_in'] = True
            st.session_state['user'] = {"email": user_email}
            st.success(f"Welcome {user_email}")
            st.rerun()
        else:
            st.error("Authentication failed. Please check your email and password.")
    except Exception as e:
        st.error(f"Authentication failed: {e}")

def send_reset_password_email(email, supabase):
    try:
        supabase.auth.reset_password_for_email(email)
        st.success("Password reset email sent. Please check your inbox.")
    except Exception as e:
        st.error(f"Failed to send password reset email: {e}")

def register_user(email, password, supabase):
        # First, check if the user already exists
    existing_user = supabase.table("users").select("*").eq("email", email).execute()
    
    if existing_user.data:
        # User already exists
        st.error("An account with this email already exists. Please use a different email or try logging in.")
        return False
    
    # If the user doesn't exist, proceed with registration
    try:
        res = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        if res.user:
            st.success("Registration successful! Please check your email to verify your account.")
            return True
        else:
            st.error("Registration failed. Please try again.")
            return False
    except Exception as e:
        st.error(f"An error occurred during registration: {str(e)}")
        return False

def auth_screen(supabase):
    # Check for existing auth token
    auth_token = get_auth_cookie()
    if auth_token:
        user_data = verify_jwt(auth_token)
        if user_data:
            st.session_state['logged_in'] = True
            st.session_state['user'] = {"email": user_data["email"]}
        else:
            st.session_state['logged_in'] = False
            clear_auth_cookie()

    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if st.session_state.get('logged_in', False):
        st.sidebar.success(f"Welcome {st.session_state['user']['email']}")
        if st.sidebar.button("Logout"):
            st.session_state['logged_in'] = False
            st.session_state.pop('user', None)
            clear_auth_cookie()
            supabase.auth.sign_out()
            st.rerun()
    else:
        auth_mode = st.radio("Select mode", ["Login", "Register"])
        st.markdown(f'## {"Welcome back!" if auth_mode == "Login" else "Create an account"}')
        
        email = st.text_input("Email", key="email")
        password = st.text_input("Password", type="password", key="password")
        
        if auth_mode == "Login":
            if st.button("Log In"):
                if is_valid_email(email):
                    authenticate_user(email, password, supabase)
                else:
                    st.error("Please enter a valid email address")
            if st.button("Forgot Password?"):
                if is_valid_email(email):
                    send_reset_password_email(email, supabase)
                else:
                    st.error("Please enter a valid email address")
        
        elif auth_mode == "Register":
            if st.button("Register"):
                if is_valid_email(email):
                    register_user(email, password, supabase)
                else:
                    st.error("Please enter a valid email address")