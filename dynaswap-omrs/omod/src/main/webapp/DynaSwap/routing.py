from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import DynaSwapApp.routing

# needed for django channels to work
application = ProtocolTypeRouter({
    # (http->django views is added by default)
    'websocket': AuthMiddlewareStack(
        URLRouter(
            DynaSwapApp.routing.websocket_urlpatterns
        )
    ),
})