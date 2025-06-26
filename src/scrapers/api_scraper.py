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

def is_domestic_stock(stock_code: str) -> bool:
    """
    주식 코드가 국내 주식인지 판단합니다.
    국내 주식: 6자리 숫자 (예: 005930, 000660)
    해외 주식: 영문 대문자 (예: AAPL, MSFT, GOOGL)
    """
    # 6자리 숫자인 경우 국내 주식
    if stock_code.isdigit() and len(stock_code) == 6:
        return True
    # 영문 대문자인 경우 해외 주식
    elif stock_code.isalpha() and stock_code.isupper():
        return False
    # 그 외의 경우는 기본적으로 국내 주식으로 간주
    else:
        return True
    
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

def get_domestic_stock_price(stock_code: str) -> Dict[str, Any]:
    """
    국내 주식의 현재가 정보를 한국투자증권 API로 조회합니다.
    """
    base_url = "https://openapi.koreainvestment.com:9443"
    url = f"{base_url}/uapi/domestic-stock/v1/quotations/inquire-price"
    
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

            # 과거 가격 및 추세
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

            # 특이사항/경고
            warning_info = {
                "투자유의여부": output.get("invt_caful_yn", ""),
                "시장경고코드": output.get("mrkt_warn_cls_code", ""),
                "관리종목여부": output.get("mang_issu_cls_code", ""),
                "정리매매여부": output.get("sltr_yn", ""),
            }

            # 기타 정보
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

            logger.info(f"{stock_code} 국내 주식 현재가 정보 조회 완료")
            return complete_info
        else:
            logger.error(f"국내 주식 현재가 조회 실패: {result.get('msg1', '알 수 없는 오류')}")
            return {}

    except Exception as e:
        logger.error(f"국내 주식 현재가 조회 중 오류 발생: {e}")
        return {}

def get_worldwide_stock_price(stock_code: str) -> Dict[str, Any]:
    """
    해외 주식의 현재가 정보를 Yahoo Finance API로 조회합니다.
    """
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{stock_code}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    params = {
        "interval": "1d",
        "range": "1d"
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()

        result = response.json()

        if result.get("chart") and result["chart"].get("result"):
            chart_data = result["chart"]["result"][0]
            meta = chart_data.get("meta", {})
            
            # 현재가 정보
            current_price = meta.get("regularMarketPrice", 0)
            previous_close = meta.get("previousClose", 0)
            
            # 등락률 계산
            if previous_close and previous_close > 0:
                change_rate = ((current_price - previous_close) / previous_close) * 100
            else:
                change_rate = 0
            
            # 거래량
            volume = meta.get("regularMarketVolume", 0)
            
            # 시가총액 (Yahoo Finance에서 제공하는 경우)
            market_cap = meta.get("marketCap", 0)
            
            # 기타 정보
            currency = meta.get("currency", "USD")
            exchange_name = meta.get("exchangeName", "")
            
            complete_info = {
                "현재가": round(current_price, 2),
                "등락률": round(change_rate, 2),
                "거래량": volume,
                "시가총액": market_cap,
                "통화": currency,
                "거래소": exchange_name,
                "이전종가": round(previous_close, 2),
            }

            logger.info(f"{stock_code} 해외 주식 현재가 정보 조회 완료")
            return complete_info
        else:
            logger.error(f"해외 주식 현재가 조회 실패: 데이터 형식 오류")
            return {}

    except Exception as e:
        logger.error(f"해외 주식 현재가 조회 중 오류 발생: {e}")
        return {}

def get_stock_current_price(stock_info: str) -> Dict[str, Any]:
    """
    주식의 현재가 정보를 조회합니다. (국내/해외 자동 구분)

    Args:
        stock_info: 종목코드 (예: "005930", "AAPL") 또는 종목명

    Returns:
        현재가 정보 딕셔너리
    """
    # 주식 코드가 국내 주식인지 해외 주식인지 판단
    if is_domestic_stock(stock_info):
        logger.info(f"{stock_info}는 국내 주식으로 판단되어 한국투자증권 API를 사용합니다.")
        return get_domestic_stock_price(stock_info)
    else:
        logger.info(f"{stock_info}는 해외 주식으로 판단되어 Yahoo Finance API를 사용합니다.")
        return get_worldwide_stock_price(stock_info)
