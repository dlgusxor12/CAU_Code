import httpx
from typing import Optional, Dict, Any
from google.auth.transport import requests
from google.oauth2 import id_token
import logging

from app.config import settings


logger = logging.getLogger(__name__)


class GoogleOAuthClient:
    """Google OAuth ID Token 검증 클라이언트"""

    def __init__(self):
        self.client_id = settings.google_client_id

    async def verify_id_token(self, id_token_string: str) -> Optional[Dict[str, Any]]:
        """
        Google ID Token을 검증하고 사용자 정보를 반환

        Args:
            id_token_string: Google에서 받은 ID Token

        Returns:
            사용자 정보 딕셔너리 또는 None (검증 실패 시)
        """
        try:
            # Google ID Token 검증
            if not self.client_id:
                logger.error("Google Client ID가 설정되지 않았습니다.")
                return None

            # ID Token 검증 및 디코딩
            id_info = id_token.verify_oauth2_token(
                id_token_string,
                requests.Request(),
                self.client_id
            )

            # 발급자 확인
            if id_info.get('iss') not in ['accounts.google.com', 'https://accounts.google.com']:
                logger.error("잘못된 토큰 발급자입니다.")
                return None

            # 필요한 정보 추출
            user_info = {
                'google_id': id_info.get('sub'),
                'email': id_info.get('email'),
                'email_verified': id_info.get('email_verified', False),
                'name': id_info.get('name'),
                'given_name': id_info.get('given_name'),
                'family_name': id_info.get('family_name'),
                'picture': id_info.get('picture'),
                'locale': id_info.get('locale')
            }

            # 필수 정보 확인
            if not user_info['google_id'] or not user_info['email']:
                logger.error("필수 사용자 정보가 누락되었습니다.")
                return None

            # 이메일 인증 확인
            if not user_info['email_verified']:
                logger.error("이메일이 인증되지 않은 계정입니다.")
                return None

            logger.info(f"Google OAuth 검증 성공: {user_info['email']}")
            return user_info

        except ValueError as e:
            logger.error(f"Google ID Token 검증 실패: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Google OAuth 검증 중 예외 발생: {str(e)}")
            return None

    async def get_user_profile(self, access_token: str) -> Optional[Dict[str, Any]]:
        """
        Google API를 사용하여 사용자 프로필 정보 조회
        (필요시 추가 정보를 위해 사용)

        Args:
            access_token: Google Access Token

        Returns:
            사용자 프로필 정보 또는 None
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://www.googleapis.com/oauth2/v2/userinfo",
                    headers={"Authorization": f"Bearer {access_token}"}
                )

                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Google 프로필 조회 실패: {response.status_code}")
                    return None

        except Exception as e:
            logger.error(f"Google 프로필 조회 중 오류: {str(e)}")
            return None

    async def verify_token_and_get_user_info(self, id_token_string: str) -> Optional[Dict[str, Any]]:
        """
        ID Token 검증 및 사용자 정보 반환 (통합 메서드)

        Args:
            id_token_string: Google ID Token

        Returns:
            검증된 사용자 정보
        """
        user_info = await self.verify_id_token(id_token_string)

        if not user_info:
            return None

        # CAU Code에서 사용할 형식으로 변환
        return {
            'google_id': user_info['google_id'],
            'email': user_info['email'],
            'name': user_info['name'] or f"{user_info.get('given_name', '')} {user_info.get('family_name', '')}".strip(),
            'profile_image_url': user_info.get('picture'),
            'locale': user_info.get('locale', 'ko')
        }


# 전역 Google OAuth 클라이언트 인스턴스
google_oauth_client = GoogleOAuthClient()