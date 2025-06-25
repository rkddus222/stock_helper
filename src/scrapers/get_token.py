#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
한국투자증권 API 토큰 발급 도구
1분 제한을 우회하기 위해 별도로 토큰을 발급받아 사용
"""
import os
import sys
import requests
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

from src.core.config import settings

load_dotenv()

def get_access_token() -> dict:
    """
    한국투자증권 API 액세스 토큰을 발급받습니다.

    Args:
        is_production: 실서버 사용 여부 (False: 모의투자, True: 실서버)

    Returns:
        토큰 정보 딕셔너리
    """

    # 환경변수에서 직접 API 키 가져오기
    app_key = os.getenv("KOR_INVESTMENT_APP_KEY")
    app_secret = os.getenv("KOR_INVESTMENT_APP_SECRET")

    if not app_key or not app_secret:
        raise ValueError("API 키가 설정되지 않았습니다. .env 파일에서 KOR_INVESTMENT_APP_KEY와 KOR_INVESTMENT_APP_SECRET을 설정해주세요.")

    base_url = "https://openapi.koreainvestment.com:9443"
    url = f"{base_url}/oauth2/tokenP"
    headers = {
        "Content-Type": "application/json"
    }

    data = {
        "grant_type": "client_credentials",
        "appkey": app_key,
        "appsecret": app_secret
    }

    try:
        print(f"토큰 발급 요청 중...")

        response = requests.post(url, headers=headers, data=json.dumps(data))

        if response.status_code == 200:
            result = response.json()

            # 만료시간 계산 (23시간 후로 설정)
            expires_at = datetime.now() + timedelta(hours=23)

            token_info = {
                "access_token": result["access_token"],
                "expires_at": expires_at.isoformat(),
                "token_type": result.get("token_type", "Bearer"),
                "expires_in": result.get("expires_in", 86400),
                "base_url": base_url,
                "is_production": True
            }

            print("✅ 토큰 발급 성공!")
            print(f"만료시간: {expires_at.strftime('%Y-%m-%d %H:%M:%S')}")

            return token_info

        else:
            print(f"❌ 토큰 발급 실패: {response.status_code}")
            print(f"응답: {response.text}")
            return None

    except Exception as e:
        print(f"❌ 토큰 발급 중 오류: {e}")
        return None


if __name__ == "__main__":
    print("=== 한국투자증권 API 토큰 발급 도구 ===\n")

    # 토큰 발급
    token_info = get_access_token()

    if token_info:
        print("\n✅ 토큰 준비 완료!")
        print(f"토큰: {token_info['access_token']}")
        print(f"만료시간: {token_info['expires_at']}")
    else:
        print("❌ 토큰 발급에 실패했습니다.")
