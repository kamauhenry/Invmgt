from .custom_tenants import get_current_tenant

class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Your custom logic to set the tenant based on the user, session, or request data
        tenant = get_current_tenant(request.user)

        if tenant is not None:
            request.tenant = tenant
            print(f"Tenant: {request.tenant}")

        response = self.get_response(request)
        return response
