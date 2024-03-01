from .models import Tenant 


def get_current_tenant(user):
    # Implement your logic to get the current tenant based on the user
    # This can vary depending on your multi-tenancy implementation
    # For example, if each user is associated with a tenant, you might do:
    try:
        return Tenant.objects.get(user=user)
    except Tenant.DoesNotExist:
        return None
