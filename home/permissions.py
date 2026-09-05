def has_content_management_access(user):
    return bool(
        user.is_authenticated
        and (
            user.is_superuser
            or getattr(user, "my_choice_field", None) == "Moderator"
            or user.has_perm("home.change_contentsection")
        )
    )
