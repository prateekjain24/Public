import streamlit as st
import os
import re
import jwt
import datetime
import json
import extra_streamlit_components as stx

SECRET_KEY = os.environ.get('SECRET_KEY')

def is_valid_email(email):
    """Validate the email format."""
    regex = r'^\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.match(regex, email)

def generate_jwt(user_email):
    expiration = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=30)
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
            # If cookie_manager doesn't find the token, try JavaScript approach
        component_value = st.components.v1.html(
                """
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
                    window.parent.Streamlit.setComponentValue(auth_token);
                }
                </script>
                """,
                height=0
            )
        if component_value is not None:
            st.session_state.auth_token = component_value
        return st.session_state.get('auth_token')

def clear_auth_cookie():
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
            st.session_state['user'] = {"email": user_email}  # Store email as a dictionary
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
    try:
        response = supabase.auth.sign_up({"email": email, "password": password})
        if response.user:
            st.success("Registration successful. Click on login to begin.")
        else:
            st.error("Registration failed. Please try again.")
    except Exception as e:
        st.error(f"Registration failed: {e}")

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

    if st.session_state['logged_in']:
        st.sidebar.success(f"Welcome {st.session_state['user']['email']}")
        if st.sidebar.button("Logout"):
            st.session_state['logged_in'] = False
            st.session_state.pop('user', None)
            clear_auth_cookie()
            supabase.auth.sign_out()
            st.rerun()
    else:
        auth_mode = st.radio("Select mode", ["Login", "Register"])
        st.markdown(f'## <div>{"Welcome back!" if auth_mode == "Login" else "Create an account"}</div>', unsafe_allow_html=True)
        
        email = st.text_input("Email", key="email", label_visibility="collapsed", placeholder="Email", help="Enter your email address")
        password = st.text_input("Password", key="password", label_visibility="collapsed", placeholder="Password", type="password", help="Enter your password")
        
        if auth_mode == "Login":
            if st.button("Log In", key="login"):
                if is_valid_email(email):
                    authenticate_user(email, password, supabase)
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