import requests
import os
from dotenv import load_dotenv
from typing import Dict, List, Optional, Any
import logging
from ..core.config import settings
from .get_token import get_access_token

# 환경변수 로드
load_dotenv()

logger = logging.getLogger(__name__)
    
def get_headers(tr_id: str) -> Dict[str, str]:
    """API 요청 헤더를 생성합니다."""

    # 환경변수에서 직접 API 키 가져오기
    app_key = os.getenv("KOR_INVESTMENT_APP_KEY")
    app_secret = os.getenv("KOR_INVESTMENT_APP_SECRET")
    
    if not app_key or not app_secret:
        raise ValueError("API 키가 설정되지 않았습니다. .env 파일에서 KOR_INVESTMENT_APP_KEY와 KOR_INVESTMENT_APP_SECRET을 설정해주세요.")
    
    token_info = get_access_token()
    if not token_info:
        raise ValueError("토큰 발급에 실패했습니다.")
    
    return {
        "Content-Type": "application/json; charset=utf-8",
        "authorization": f"Bearer {token_info['access_token']}",
        "appKey": app_key,
        "appSecret": app_secret,
        "tr_id": tr_id
    }

def get_stock_current_price(stock_info: str) -> Dict[str, Any]:
    """
    특정 주식의 현재가 정보를 조회합니다.

    Args:
        stock_info: 종목코드 (예: "005930") 또는 종목명 (예: "삼성전자")

    Returns:
        현재가 정보 딕셔너리
    """
    base_url = "https://openapi.koreainvestment.com:9443"
    url = f"{base_url}/uapi/domestic-stock/v1/quotations/inquire-price"
    stock_code = stock_info
    
    params = {
        "FID_COND_MRKT_DIV_CODE": "J",
        "FID_INPUT_ISCD": stock_code
    }

    headers = get_headers("FHKST01010100")

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()

        result = response.json()

        if result["rt_cd"] == "0" and result.get("output"):
            output = result["output"]

            # 현재가 및 가격 변동
            current_price_info = {
                "현재가": int(output.get("stck_prpr", 0)),
                "등락률": float(output.get("prdy_ctrt", 0)),
            }

            # 거래량 및 거래대금
            volume_info = {
                "거래량": int(output.get("acml_vol", 0)),
                "거래대금": int(output.get("acml_tr_pbmn", 0)),
                "거래량회전율": float(output.get("vol_tnrt", 0)),
            }

            # 기업 가치 지표
            valuation_info = {
                "시가총액": int(output.get("hts_avls", 0)),
                "PER": float(output.get("per", 0)),
                "PBR": float(output.get("pbr", 0)),
            }

            # 과거 가격 및 추세 (주요 장기/단기 최고/최저가만)
            historical_info = {
                "250일최고가": int(output.get("d250_hgpr", 0)),
                "250일최저가": int(output.get("d250_lwpr", 0)),
                "52주최고가": int(output.get("w52_hgpr", 0)),
                "52주최저가": int(output.get("w52_lwpr", 0)),
            }

            # 투자자 동향
            investor_info = {
                "외국인순매수수량": int(output.get("frgn_ntby_qty", 0)),
                "프로그램매매순매수수량": int(output.get("pgtr_ntby_qty", 0)),
            }

            # 특이사항/경고 (투자 결정에 중요한 요소만)
            warning_info = {
                "투자유의여부": output.get("invt_caful_yn", ""),
                "시장경고코드": output.get("mrkt_warn_cls_code", ""),
                "관리종목여부": output.get("mang_issu_cls_code", ""),
                "정리매매여부": output.get("sltr_yn", ""),
            }

            # 기타 정보 (업종 및 시장 구분)
            other_info = {
                "업종명": output.get("bstp_kor_isnm", ""),
                "시장구분": output.get("rprs_mrkt_kor_name", ""),
            }

            # 모든 정보를 하나의 딕셔너리로 통합
            complete_info = {
                **current_price_info,
                **volume_info,
                **valuation_info,
                **historical_info,
                **investor_info,
                **warning_info,
                **other_info
            }

            logger.info(f"{stock_code} 종목의 상세 현재가 정보 조회 완료")
            return complete_info
        else:
            logger.error(f"현재가 조회 실패: {result.get('msg1', '알 수 없는 오류')}")
            return {}

    except Exception as e:
        logger.error(f"현재가 조회 중 오류 발생: {e}")
        return {}
