import httpx
from fastapi import HTTPException

from src.core.constants import WEB_CLIENT_ID, MOBILE_CLIENT_ID, WEB_REDIRECT_URI, MOBILE_REDIRECT_URI


async def decode_vk_id(code_verifier: str, code: str, device_id: str, state: str, from_web: bool) -> int:
    """
    Определяет ВкАйди из секртеного кода
    :param code_verifier: ПКСЕ-параметры
    :param code:
    :param device_id:
    :param state:
    :param from_web: Со стороны веба (истина) или от мобильного приложения (ложь)
    :return: ВкАйди пользовталя
    """
    url = "https://id.vk.com/oauth2/auth"

    if from_web:
        data = {
            "grant_type": "authorization_code",
            "code_verifier": code_verifier,
            "redirect_uri": WEB_REDIRECT_URI,
            "code": code,
            "client_id": WEB_CLIENT_ID,
            "device_id": device_id,
            "state": state
        }
    else:
        data = {
            "grant_type": "authorization_code",
            "code_verifier": code_verifier,
            "redirect_uri": MOBILE_REDIRECT_URI,
            "code": code,
            "client_id": MOBILE_CLIENT_ID,
            "device_id": device_id,
            "state": state
        }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=data)

    if response.status_code == 200:
        return response.json().get('user_id')
    else:
        raise HTTPException(400, response.json().get('error_description'))
