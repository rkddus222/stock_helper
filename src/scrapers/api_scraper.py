import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class KoreaInvestmentAPIScraper:
    """
    한국투자증권 API를 사용하여 주식 일별 가격 데이터를 가져오는 스크래퍼
    주식 분석을 위한 OHLCV 데이터 제공
    """
    
    def __init__(self, app_key: str, app_secret: str, is_production: bool = False):
        """
        한국투자증권 API 스크래퍼 초기화
        
        Args:
            app_key: 한국투자증권에서 발급받은 앱키
            app_secret: 한국투자증권에서 발급받은 앱시크릿
            is_production: 실서버 사용 여부 (False: 모의투자, True: 실서버)
        """
        self.app_key = app_key
        self.app_secret = app_secret
        self.is_production = is_production
        
        # API URL 설정
        if is_production:
            self.base_url = "https://openapi.koreainvestment.com:9443"
        else:
            self.base_url = "https://openapivts.koreainvestment.com:29443"
        
        # 토큰 정보
        self.access_token = None
        self.token_expires_at = None
    
    def _get_access_token(self) -> str:
        """액세스 토큰을 발급받거나 갱신합니다."""
        if (self.access_token and self.token_expires_at and 
            datetime.now() < self.token_expires_at):
            return self.access_token
        
        url = f"{self.base_url}/oauth2/tokenP"
        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "grant_type": "client_credentials",
            "appkey": self.app_key,
            "appsecret": self.app_secret
        }
        
        try:
            response = requests.post(url, headers=headers, data=json.dumps(data))
            response.raise_for_status()
            
            result = response.json()
            self.access_token = result["access_token"]
            # 토큰 만료시간 설정 (23시간 후로 설정)
            self.token_expires_at = datetime.now() + timedelta(hours=23)
            
            logger.info("액세스 토큰 발급 완료")
            return self.access_token
            
        except Exception as e:
            logger.error(f"액세스 토큰 발급 실패: {e}")
            raise
    
    def _get_headers(self, tr_id: str) -> Dict[str, str]:
        """API 요청 헤더를 생성합니다."""
        token = self._get_access_token()
        return {
            "Content-Type": "application/json; charset=UTF-8",
            "authorization": f"Bearer {token}",
            "appKey": self.app_key,
            "appSecret": self.app_secret,
            "tr_id": tr_id
        }
    
    def get_stock_daily_price(self, stock_code: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        특정 주식의 일별 가격 정보를 조회합니다. (OHLCV 데이터)
        주식 분석에 가장 중요한 기능입니다.
        
        Args:
            stock_code: 종목코드 (예: "005930" for 삼성전자)
            start_date: 시작일 (YYYYMMDD)
            end_date: 종료일 (YYYYMMDD)
            
        Returns:
            일별 가격 정보 리스트 (OHLCV 데이터)
        """
        url = f"{self.base_url}/uapi/domestic-stock/v1/quotations/inquire-daily-price"
        
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code,
            "FID_INPUT_DATE_1": start_date,
            "FID_INPUT_DATE_2": end_date,
            "FID_VOL_CNT": "100"
        }
        
        headers = self._get_headers("FHKST01010400")
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            result = response.json()
            
            if result["rt_cd"] == "0":
                output = result["output"]
                daily_prices = []
                
                for item in output:
                    daily_prices.append({
                        "날짜": item["stck_bsop_date"],
                        "시가": int(item["stck_oprc"]),
                        "고가": int(item["stck_hgpr"]),
                        "저가": int(item["stck_lwpr"]),
                        "종가": int(item["stck_clpr"]),
                        "거래량": int(item["cntg_vol"]),
                        "거래대금": int(item["acml_tr_pbmn"]),
                        "등락률": float(item["prdy_ctrt"]),
                        "등락금액": int(item["prdy_vrss"])
                    })
                
                # 날짜순으로 정렬 (최신순)
                daily_prices.sort(key=lambda x: x["날짜"], reverse=True)
                
                logger.info(f"{stock_code} 종목의 {len(daily_prices)}일간 일별 가격 데이터 조회 완료")
                return daily_prices
            else:
                logger.error(f"일별 가격 조회 실패: {result['msg1']}")
                return []
                
        except Exception as e:
            logger.error(f"일별 가격 조회 중 오류 발생: {e}")
            return []
    
    def get_stock_search(self, keyword: str) -> List[Dict[str, Any]]:
        """
        종목명으로 주식 검색을 수행합니다.
        일별 가격 데이터를 조회하기 전에 종목코드를 찾기 위해 필요합니다.
        
        Args:
            keyword: 검색할 종목명 키워드
            
        Returns:
            검색 결과 리스트
        """
        url = f"{self.base_url}/uapi/domestic-stock/v1/quotations/inquire-search"
        
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_COND_SCR_DIV_CODE": "20171",
            "FID_INPUT_ISCD": keyword
        }
        
        headers = self._get_headers("FHKST01010300")
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            result = response.json()
            
            if result["rt_cd"] == "0":
                output = result["output"]
                search_results = []
                
                for item in output:
                    search_results.append({
                        "종목코드": item["hts_kor_isnm"],
                        "종목명": item["hts_kor_isnm"],
                        "시장구분": item["rprs_mrkt_kor_name"]
                    })
                
                return search_results
            else:
                logger.error(f"종목 검색 실패: {result['msg1']}")
                return []
                
        except Exception as e:
            logger.error(f"종목 검색 중 오류 발생: {e}")
            return []
