# passwords = {"bediamonds": "e49c333119eb701c2530763d715e7130e07569bcdfe09da586aa6f3d3e87431a"}
# unrestricted_page_routes = {"/login"}


# class AuthMiddleware(BaseHTTPMiddleware):
#     """This middleware restricts access to all NiceGUI pages.

#     It redirects the user to the login page if they are not authenticated.
#     """

#     async def dispatch(self, request: Request, call_next):
#         if not app.storage.user.get("authenticated", False):
#             if request.url.path in Client.page_routes.values() and request.url.path not in unrestricted_page_routes:
#                 app.storage.user["referrer_path"] = request.url.path  # remember where the user wanted to go
#                 return RedirectResponse("/login")
#         return await call_next(request)


# app.add_middleware(AuthMiddleware)


# @ui.page("/login")
# def login() -> Optional[RedirectResponse]:
#     def try_login() -> None:  # local function to avoid passing username and password as arguments
#         hash_pw = utils.hash_password(password.value)
#         if passwords.get(username.value) == hash_pw:
#             app.storage.user.update({"username": username.value, "authenticated": True})
#             ui.navigate.to(app.storage.user.get("referrer_path", "/"))  # go back to where the user wanted to go
#         else:
#             ui.notify("Wrong username or password", color="negative")

#     if app.storage.user.get("authenticated", False):
#         return RedirectResponse("/")
#     with ui.card().classes("absolute-center"):
#         username = ui.input("Username").on("keydown.enter", try_login)
#         password = ui.input("Password", password=True, password_toggle_button=True).on("keydown.enter", try_login)
#         ui.button("Log in", on_click=try_login)
#     return None