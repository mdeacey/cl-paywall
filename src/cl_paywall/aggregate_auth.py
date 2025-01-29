import chainlit as cl
import os
from .google_auth import get_logged_in_user_email, show_login_button
from .stripe_auth import is_active_subscriber, redirect_button
from .buymeacoffee_auth import get_bmac_payers

payment_provider = os.getenv("PAYMENT_PROVIDER", "stripe")

async def add_auth(
    required: bool = True,
    login_button_text: str = "Login with Google",
    login_button_color: str = "#FD504D",
    login_sidebar: bool = True,
):
    if required:
        await require_auth(
            login_button_text=login_button_text,
            login_sidebar=login_sidebar,
            login_button_color=login_button_color,
        )
    else:
        await optional_auth(
            login_button_text=login_button_text,
            login_sidebar=login_sidebar,
            login_button_color=login_button_color,
        )

async def require_auth(
    login_button_text: str = "Login with Google",
    login_button_color: str = "#FD504D",
    login_sidebar: bool = True,
):
    user_email = get_logged_in_user_email()

    if not user_email:
        await show_login_button(
            text=login_button_text, color=login_button_color, sidebar=login_sidebar
        )
        return

    if payment_provider == "stripe":
        is_subscriber = user_email and is_active_subscriber(user_email)
    elif payment_provider == "bmac":
        is_subscriber = user_email and user_email in get_bmac_payers()
    else:
        raise ValueError("payment_provider must be 'stripe' or 'bmac'")

    if not is_subscriber:
        await redirect_button(
            text="Subscribe now!",
            customer_email=user_email,
            payment_provider=payment_provider,
        )
        cl.user_session.set("user_subscribed", False)
        return
    
    cl.user_session.set("user_subscribed", True)
    
    if await cl.AskUserActionMessage(content="Logout?", actions=["Logout"]).send():
        cl.user_session.clear()
        await cl.Message(content="You have been logged out.").send()

async def optional_auth(
    login_button_text: str = "Login with Google",
    login_button_color: str = "#FD504D",
    login_sidebar: bool = True,
):
    user_email = get_logged_in_user_email()
    
    if payment_provider == "stripe":
        is_subscriber = user_email and is_active_subscriber(user_email)
    elif payment_provider == "bmac":
        is_subscriber = user_email and user_email in get_bmac_payers()
    else:
        raise ValueError("payment_provider must be 'stripe' or 'bmac'")

    if not user_email:
        await show_login_button(
            text=login_button_text, color=login_button_color, sidebar=login_sidebar
        )
        cl.user_session.set("email", "")
    
    if not is_subscriber:
        await redirect_button(
            text="Subscribe now!", customer_email="", payment_provider=payment_provider
        )
        cl.user_session.set("user_subscribed", False)
    else:
        cl.user_session.set("user_subscribed", True)
    
    if cl.user_session.get("email") and await cl.AskUserActionMessage(content="Logout?", actions=["Logout"]).send():
        cl.user_session.clear()
        await cl.Message(content="You have been logged out.").send()
