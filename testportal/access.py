CATEGORY_MANAGER_GROUP_NAME = 'Category Managers'


def can_manage_categories(user):
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return user.groups.filter(name=CATEGORY_MANAGER_GROUP_NAME).exists()
