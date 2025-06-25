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
from dotenv import load_dotenv, set_key
from pathlib import Path

from src.core.config import settings

# 프로젝트 루트 디렉토리 찾기
project_root = Path(__file__).parent.parent.parent
env_file_path = project_root / '.env'

load_dotenv(env_file_path)

def save_token_to_env(token_info: dict):
    """
    토큰 정보를 .env 파일에 저장합니다.
    """
    try:
        # .env 파일에 토큰 정보 저장 (절대 경로 사용)
        set_key(env_file_path, 'KOR_INVESTMENT_ACCESS_TOKEN', token_info['access_token'])
        set_key(env_file_path, 'KOR_INVESTMENT_TOKEN_EXPIRES_AT', token_info['expires_at'])
        set_key(env_file_path, 'KOR_INVESTMENT_TOKEN_TYPE', token_info['token_type'])
        
        print(f"✅ 토큰 정보가 {env_file_path} 파일에 저장되었습니다.")
        return True
    except Exception as e:
        print(f"❌ 토큰 저장 중 오류: {e}")
        return False

def is_token_expired() -> bool:
    """
    저장된 토큰의 만료 시간을 확인합니다.
    """
    expires_at_str = os.getenv("KOR_INVESTMENT_TOKEN_EXPIRES_AT")
    if not expires_at_str:
        return True
    
    try:
        expires_at = datetime.fromisoformat(expires_at_str)
        # 10분 여유를 두고 만료 체크
        return datetime.now() >= (expires_at - timedelta(minutes=10))
    except Exception as e:
        print(f"토큰 만료 시간 파싱 오류: {e}")
        return True

def get_saved_token() -> dict:
    """
    저장된 토큰 정보를 반환합니다.
    """
    access_token = os.getenv("KOR_INVESTMENT_ACCESS_TOKEN")
    expires_at = os.getenv("KOR_INVESTMENT_TOKEN_EXPIRES_AT")
    token_type = os.getenv("KOR_INVESTMENT_TOKEN_TYPE", "Bearer")
    
    if access_token and expires_at:
        return {
            "access_token": access_token,
            "expires_at": expires_at,
            "token_type": token_type,
            "base_url": "https://openapi.koreainvestment.com:9443",
            "is_production": True
        }
    return None

def get_access_token() -> dict:
    """
    한국투자증권 API 액세스 토큰을 발급받습니다.
    저장된 토큰이 있고 만료되지 않았다면 그것을 사용하고,
    만료되었다면 새로 발급받아 저장합니다.

    Returns:
        토큰 정보 딕셔너리
    """
    # 먼저 저장된 토큰이 있는지 확인
    saved_token = get_saved_token()
    if saved_token and not is_token_expired():
        print("✅ 저장된 토큰을 사용합니다.")
        return saved_token
    
    print("🔄 토큰이 만료되었거나 없습니다. 새로 발급받습니다...")

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

            # 토큰을 .env 파일에 저장
            if save_token_to_env(token_info):
                print("✅ 토큰 발급 및 저장 성공!")
                print(f"만료시간: {expires_at.strftime('%Y-%m-%d %H:%M:%S')}")
                return token_info
            else:
                print("⚠️ 토큰 발급은 성공했지만 저장에 실패했습니다.")
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
