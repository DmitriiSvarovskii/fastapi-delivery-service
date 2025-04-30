from .packages import router as packages_router
from .package_types import router as package_types_router

routers = (
    package_types_router,
    packages_router,
)
