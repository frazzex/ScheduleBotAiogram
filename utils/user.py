from models import User

async def get_or_create_user(user_id: int, username: str = None, full_name: str = None) -> User:
    """Получить или создать пользователя"""
    user, created = await User.get_or_create(
        id=user_id,
        defaults={
            'username': username,
            'full_name': full_name
        }
    )
    if not created:
        # Обновляем данные, если они изменились
        if username and user.username != username:
            user.username = username
        if full_name and user.full_name != full_name:
            user.full_name = full_name
        await user.save()
    return user