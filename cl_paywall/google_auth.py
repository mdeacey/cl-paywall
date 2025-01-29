import asyncio
import os
from typing import Optional
import jwt
import chainlit as cl
from httpx_oauth.clients.google import GoogleOAuth2
from httpx_oauth.oauth2 import OAuth2Token

# Load secrets from environment variables
testing_mode = os.getenv("TESTING_MODE", "False").lower() == "true"
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
redirect_url = os.getenv("REDIRECT_URL_TEST") if testing_mode else os.getenv("REDIRECT_URL")

client = GoogleOAuth2(client_id=client_id, client_secret=client_secret)

def decode_user(token: str):
    """
    Decodes a JWT token to extract user information.
    """
    decoded_data = jwt.decode(jwt=token, options={"verify_signature": False})
    return decoded_data

async def get_authorization_url() -> str:
    authorization_url = await client.get_authorization_url(
        redirect_url,
        scope=["email"],
        extras_params={"access_type": "offline"},
    )
    return authorization_url

async def get_access_token(code: str) -> OAuth2Token:
    token = await client.get_access_token(code, redirect_url)
    return token

def get_access_token_from_query_params() -> Optional[OAuth2Token]:
    code = cl.user_session.get("auth_code")
    if not code:
        return None
    
    token = asyncio.run(get_access_token(code))
    cl.user_session.set("auth_code", None)  # Clear stored auth code
    return token

async def show_login_button(text: Optional[str] = "Login with Google", color="#FD504D"):
    authorization_url = await get_authorization_url()
    await cl.Message(content=f"[**{text}**]({authorization_url})", author="system").send()

def get_logged_in_user_email() -> Optional[str]:
    if cl.user_session.get("email"):
        return cl.user_session.get("email")
    
    token_from_params = get_access_token_from_query_params()
    if not token_from_params:
        return None
    
    user_info = decode_user(token=token_from_params["id_token"])
    cl.user_session.set("email", user_info["email"])
    return user_info["email"]
