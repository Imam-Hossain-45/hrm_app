from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import ImproperlyConfigured


class PermissionMixin(PermissionRequiredMixin):
    """User permission verification."""

    permission_denied_message = 'You do not have permission for this action'
    permission_required = None
    strict_mode = False

    def get_current_user_permission_groups(self):
        """Get all the permission group of the current user."""

        permissions = self.request.user.usergroup_set.all()

        return list(permission.group for permission in permissions)

    def get_current_user_permission_list(self):
        """Get all the permission of the current user."""

        permissions = []
        permission_list = self.request.user.usergroup_set.all()

        for permission in permission_list:
            permissions += list(map(lambda perm: perm.codename, permission.group.permissions.all()))

        return permissions

    def get_permission_required(self):
        """Collect permission required property and convert to a list."""

        if self.permission_required is None:
            raise ImproperlyConfigured(
                '{0} is missing the permission_required attribute. Define {0}.permission_required, or override '
                '{0}.get_permission_required().'.format(self.__class__.__name__)
            )

        if isinstance(self.permission_required, str):
            perms = [self.permission_required]
        else:
            perms = self.permission_required
        return perms

    def has_permission(self):
        """Verify that the current user has all specified permissions."""

        if self.permission_required is None:
            return True

        if self.request.user.is_superuser:
            return True

        permissions = list(filter(
            lambda perm: perm in self.permission_required, self.get_current_user_permission_list()
        ))

        if self.strict_mode and len(permissions) < len(self.permission_required):
            return False
        elif len(permissions) == 0:
            return False

        return True
