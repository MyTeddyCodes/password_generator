from state import active_session
from datetime import datetime, timedelta
from fastapi import Request, HTTPException
from fastapi.responses import RedirectResponse
from functools import wraps
import secrets


def create_session(user_id: int, master_password: str) -> str:
    """Create a new session for user"""
    session_token = secrets.token_urlsafe(32)
    active_session[session_token] = {
        "user_id": user_id,
        "master_password": master_password,  # ONLY in memory!
        "created_at": datetime.now()
    }
    print(active_session)
    return session_token


def get_current_session(request: Request):
    """Get the current session if valid"""
    session_token = request.cookies.get("session_token")
    if not session_token:
        print("No Session_Token")
        return None

    session = active_session.get(session_token)
    print(f'active session: = > {active_session}')
    if not session:
        print("No active session")
        return None
    else:
        print(f'time, {datetime.now() - session["created_at"]}')

    # Check if session expired (optional)
    if (datetime.now() - session["created_at"]) > timedelta(hours=2):
        print(f'\ntime before delete, {
              datetime.now() - session["created_at"]}')
        del active_session[session_token]

        print("Session expired")
        return None

    session["created_at"] = datetime.now()

    return session


def login_required(api_route=False):
    """Decorator to require Login"""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Check if user has active session
            request: Request = kwargs.get("request")
            if not request:
                raise RuntimeError(
                    "Route must include 'request: Request' to use login_required")

            session = get_current_session(request)

            if not session:
                # No active session - block access
                if api_route:
                    # API route
                    raise HTTPException(
                        status_code=401, detail="Please login first")
                else:
                    # HTML route
                    return RedirectResponse(url="/login_form", status_code=303)

            # Add session to kwargs and call the function
            import inspect
            sig = inspect.signature(func)
            if 'session' in sig.parameters:
                kwargs['session'] = session

            # ONLY pass kwargs. Do not pass 'request' or '*args' separately.
            return await func(**kwargs)
        return wrapper
    return decorator
