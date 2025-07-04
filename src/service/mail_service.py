import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional
import re

class EmailService:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = os.getenv('SENDER_EMAIL')
        self.sender_password = os.getenv('SENDER_PASSWORD')
        self.recipient_email = os.getenv('RECIPIENT_EMAIL')
        
    def send_analysis_report(self, final_analyzed_data: str, proposed_data: str = "", stock_data: str = "", scraped_data: str = "", proposed_domestic_data: str = "", proposed_worldwide_data: str = "") -> bool:
        """
        분석 결과를 이메일로 전송합니다.
        
        Args:
            final_analyzed_data: 최종 분석 결과
            proposed_data: 추천 종목 데이터
            stock_data: 주식 데이터 (선택사항)
            scraped_data: 스크랩된 뉴스 데이터 (선택사항)
            proposed_domestic_data: 국내 추천 종목 데이터 (선택사항)
            proposed_worldwide_data: 해외 추천 종목 데이터 (선택사항)
            
        Returns:
            bool: 전송 성공 여부
        """
        try:
            if not all([self.sender_email, self.sender_password, self.recipient_email]):
                print("⚠️  이메일 설정이 완료되지 않았습니다. 환경변수를 확인해주세요.")
                print("필요한 환경변수: SENDER_EMAIL, SENDER_PASSWORD, RECIPIENT_EMAIL")
                return False
            
            # 이메일 메시지 생성
            msg = MIMEMultipart('alternative')
            msg['From'] = self.sender_email
            msg['To'] = self.recipient_email
            msg['Subject'] = f"📊 주식 시장 분석 보고서 - {datetime.now().strftime('%Y년 %m월 %d일 %H:%M')}"
            
            # HTML 이메일 본문 생성
            html_body = self._create_html_email_body(final_analyzed_data, proposed_data, stock_data, scraped_data, proposed_domestic_data, proposed_worldwide_data)
            text_body = self._create_text_email_body(final_analyzed_data, proposed_data, stock_data, scraped_data, proposed_domestic_data, proposed_worldwide_data)
            
            # HTML과 텍스트 버전 모두 첨부
            msg.attach(MIMEText(text_body, 'plain', 'utf-8'))
            msg.attach(MIMEText(html_body, 'html', 'utf-8'))
            
            # SMTP 서버 연결 및 이메일 전송
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            print(f"✅ 분석 보고서가 {self.recipient_email}로 성공적으로 전송되었습니다.")
            return True
            
        except Exception as e:
            print(f"❌ 이메일 전송 실패: {str(e)}")
            return False
    
    def _create_html_email_body(self, final_analyzed_data: str, proposed_data: str, stock_data: str, scraped_data: str, proposed_domestic_data: str, proposed_worldwide_data: str) -> str:
        """
        HTML 형식의 이메일 본문을 생성합니다.
        """
        # 분석 데이터를 HTML로 변환
        html_analysis = self._convert_analysis_to_html(final_analyzed_data)
        html_proposed = self._convert_proposed_to_html(proposed_data) if proposed_data else ""
        html_domestic = self._convert_raw_data_to_html(proposed_domestic_data, "🇰🇷 국내 추천 종목") if proposed_domestic_data else ""
        html_worldwide = self._convert_raw_data_to_html(proposed_worldwide_data, "🌍 해외 추천 종목") if proposed_worldwide_data else ""
        
        html_template = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>주식 시장 분석 보고서</title>
</head>
<body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; background-color: #f5f5f5;">
    <div style="background-color: white; border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); overflow: hidden;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center;">
            <h1 style="margin: 0; font-size: 28px; font-weight: 300;">📈 주식 시장 분석 보고서</h1>
            <div style="margin-top: 10px; opacity: 0.9; font-size: 16px;">{datetime.now().strftime('%Y년 %m월 %d일 %H:%M')}</div>
        </div>
        
        <div style="padding: 30px;">
            {html_analysis}
            
            {html_proposed}
            
            {html_domestic}
            
            {html_worldwide}
            
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 6px; border: 1px solid #dee2e6; margin-top: 20px; font-size: 14px; color: #6c757d;">
                <strong>⚠️ 투자 주의사항:</strong><br>
                본 보고서는 AI 기반 주식 분석 시스템에 의해 자동 생성되었습니다. 
                투자 결정 시 추가적인 검토와 전문가 상담을 권장합니다. 
                과거 성과가 미래 수익을 보장하지 않으며, 투자는 본인의 판단과 책임 하에 이루어져야 합니다.
            </div>
        </div>
        
        <div style="background-color: #34495e; color: white; padding: 20px; text-align: center; font-size: 14px;">
            <p style="margin: 0 0 10px 0;">🤖 AI 주식 분석 시스템 | 자동 생성 보고서</p>
            <p style="margin: 0;">© 2024 Stock Helper. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
        """
        
        return html_template
    
    def _convert_analysis_to_html(self, analysis_data: str) -> str:
        """
        분석 데이터를 HTML로 변환합니다.
        """
        if not analysis_data:
            return ""
        
        # 섹션별로 분리
        sections = analysis_data.split('\n\n')
        html_sections = []
        
        for section in sections:
            if not section.strip():
                continue
                
            lines = section.strip().split('\n')
            if not lines:
                continue
                
            title = lines[0].strip()
            content = '\n'.join(lines[1:]).strip()
            
            # 제목에서 이모지 제거하고 정리
            clean_title = title.replace('📊', '').replace('=', '').strip()
            
            if '시장 분석' in clean_title:
                icon = "🌍"
            elif '투자 전략' in clean_title:
                icon = "🎯"
            elif '개별 주식' in clean_title:
                icon = "📈"
            else:
                icon = "📊"
            
            # 내용을 HTML로 변환
            html_content = self._convert_text_to_html(content)
            
            html_sections.append(f"""
            <div style="margin-bottom: 30px;">
                <div style="color: #2c3e50; font-size: 20px; font-weight: 600; margin-bottom: 15px; padding-bottom: 10px; border-bottom: 2px solid #3498db;">
                    {icon} {clean_title}
                </div>
                {html_content}
            </div>
            """)
        
        return '\n'.join(html_sections)
    
    def _convert_proposed_to_html(self, proposed_data: str) -> str:
        """
        추천 종목 데이터를 HTML로 변환합니다.
        """
        if not proposed_data:
            return ""
        
        # 추천 종목 정보를 파싱하여 HTML로 변환
        lines = proposed_data.split('\n')
        html_items = []
        
        current_stock_name = ""
        current_stock_code = ""
        current_reason = ""
        current_opinion = ""
        current_price = ""
        current_target = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 섹션 제목 확인
            if line.startswith('##'):
                # 이전 종목 정보가 있으면 HTML 생성
                if current_stock_name:
                    html_items.append(self._create_stock_item_html(
                        current_stock_name, current_stock_code, current_reason, 
                        current_opinion, current_price, current_target
                    ))
                    # 변수 초기화
                    current_stock_name = ""
                    current_stock_code = ""
                    current_reason = ""
                    current_opinion = ""
                    current_price = ""
                    current_target = ""
                continue
            
            # 새로운 종목 시작 (숫자. **종목명** 형식)
            if re.match(r'^\d+\.\s*\*\*.*\*\*', line):
                # 이전 종목 정보가 있으면 HTML 생성
                if current_stock_name:
                    html_items.append(self._create_stock_item_html(
                        current_stock_name, current_stock_code, current_reason, 
                        current_opinion, current_price, current_target
                    ))
                
                # 종목명과 코드 추출
                stock_match = re.search(r'\*\*(.*?)\*\*', line)
                if stock_match:
                    current_stock_name = stock_match.group(1)
                    # 괄호 안의 코드 추출
                    code_match = re.search(r'\(([^)]+)\)', line)
                    current_stock_code = code_match.group(1) if code_match else ""
                    # 변수 초기화
                    current_reason = ""
                    current_opinion = ""
                    current_price = ""
                    current_target = ""
            
            # 추천 사유 확인
            elif line.startswith('- **추천 사유**:') or line.startswith('* **추천 사유**:'):
                current_reason = line.replace('- **추천 사유**:', '').replace('* **추천 사유**:', '').strip()
            
            # 투자 의견 확인
            elif line.startswith('- **투자 의견**:') or line.startswith('* **투자 의견**:'):
                current_opinion = line.replace('- **투자 의견**:', '').replace('* **투자 의견**:', '').strip()
            
            # 현재가 확인
            elif line.startswith('- **현재가**:') or line.startswith('* **현재가**:'):
                current_price = line.replace('- **현재가**:', '').replace('* **현재가**:', '').strip()
            
            # 목표가 확인
            elif line.startswith('- **목표가**:') or line.startswith('* **목표가**:'):
                current_target = line.replace('- **목표가**:', '').replace('* **목표가**:', '').strip()
        
        # 마지막 종목 처리
        if current_stock_name:
            html_items.append(self._create_stock_item_html(
                current_stock_name, current_stock_code, current_reason, 
                current_opinion, current_price, current_target
            ))
        
        if html_items:
            return f"""
            <div style="margin-bottom: 30px;">
                <div style="color: #2c3e50; font-size: 20px; font-weight: 600; margin-bottom: 15px; padding-bottom: 10px; border-bottom: 2px solid #3498db;">
                    🎯 추천 종목 정보
                </div>
                {''.join(html_items)}
            </div>
            """
        
        return ""
    
    def _create_stock_item_html(self, stock_name: str, stock_code: str, reason: str, opinion: str, price: str, target: str) -> str:
        """
        개별 종목 HTML을 생성합니다.
        """
        # 투자 의견에 따른 스타일 결정
        bg_color = "#ecf0f1"
        border_color = "#e74c3c"
        
        if opinion:
            if '매수' in opinion:
                bg_color = "#d5f4e6"
                border_color = "#27ae60"
            elif '매도' in opinion:
                bg_color = "#fadbd8"
                border_color = "#e74c3c"
            elif '보유' in opinion or '관망' in opinion:
                bg_color = "#fef9e7"
                border_color = "#f39c12"
        
        html = f'<div style="background-color: {bg_color}; padding: 15px; margin: 10px 0; border-radius: 6px; border-left: 4px solid {border_color};">'
        html += f'<div style="font-weight: bold; color: #2c3e50; font-size: 16px;">{stock_name}'
        if stock_code:
            html += f' <span style="color: #7f8c8d; font-size: 14px; font-weight: normal;">({stock_code})</span>'
        html += '</div>'
        
        if reason:
            html += f'<div style="margin-top: 8px; color: #7f8c8d;"><strong>추천 사유:</strong> {reason}</div>'
        
        if opinion:
            html += f'<div style="margin-top: 8px; color: #7f8c8d;"><strong>투자 의견:</strong> {opinion}</div>'
        
        if price:
            html += f'<div style="margin-top: 8px; color: #7f8c8d;"><strong>현재가:</strong> <span style="color: #e74c3c; font-weight: bold;">{price}</span></div>'
        
        if target:
            html += f'<div style="margin-top: 8px; color: #7f8c8d;"><strong>목표가:</strong> <span style="color: #e74c3c; font-weight: bold;">{target}</span></div>'
        
        html += '</div>'
        return html
    
    def _convert_raw_data_to_html(self, raw_data: str, title: str) -> str:
        """
        원시 데이터를 HTML로 변환합니다.
        """
        if not raw_data:
            return ""
        
        # 텍스트를 HTML로 변환
        html_content = self._convert_text_to_html(raw_data)
        
        return f"""
        <div style="margin-bottom: 30px;">
            <div style="color: #2c3e50; font-size: 20px; font-weight: 600; margin-bottom: 15px; padding-bottom: 10px; border-bottom: 2px solid #3498db;">
                {title}
            </div>
            {html_content}
        </div>
        """
    
    def _convert_text_to_html(self, text: str) -> str:
        """
        일반 텍스트를 HTML로 변환합니다.
        """
        if not text:
            return ""
        
        # 줄바꿈을 <br>로 변환
        html = text.replace('\n', '<br>')
        
        # 강조 표시
        html = html.replace('**', '<strong>').replace('**', '</strong>')
        
        # 가격 정보 강조
        import re
        price_pattern = r'(\d{1,3}(?:,\d{3})*원)'
        html = re.sub(price_pattern, r'<span style="color: #e74c3c; font-weight: bold;">\1</span>', html)
        
        # 긍정/부정 키워드 강조
        positive_words = ['상승', '매수', '긍정', '호재', '성장']
        negative_words = ['하락', '매도', '부정', '악재', '위험']
        
        for word in positive_words:
            html = html.replace(word, f'<span style="color: #27ae60;">{word}</span>')
        
        for word in negative_words:
            html = html.replace(word, f'<span style="color: #e74c3c;">{word}</span>')
        
        return f'<div style="margin-bottom: 20px; padding: 15px; background-color: #f8f9fa; border-radius: 8px; border-left: 4px solid #3498db;">{html}</div>'
    
    def _create_text_email_body(self, final_analyzed_data: str, proposed_data: str, stock_data: str, scraped_data: str, proposed_domestic_data: str, proposed_worldwide_data: str) -> str:
        """
        텍스트 형식의 이메일 본문을 생성합니다 (HTML을 지원하지 않는 클라이언트용).
        """
        body = f"""
주식 시장 분석 보고서
생성 시간: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M:%S')}

{'='*50}

📊 최종 분석 결과
{'='*50}
{final_analyzed_data}

"""
        
        if proposed_data:
            body += f"""
{'='*50}
🎯 추천 종목 정보
{'='*50}
{proposed_data}

"""
        
        if proposed_domestic_data:
            body += f"""
{'='*50}
🇰🇷 국내 추천 종목
{'='*50}
{proposed_domestic_data}

"""
        
        if proposed_worldwide_data:
            body += f"""
{'='*50}
🌍 해외 추천 종목
{'='*50}
{proposed_worldwide_data}

"""
        
        body += f"""
{'='*50}
본 보고서는 AI 기반 주식 분석 시스템에 의해 자동 생성되었습니다.
투자 결정 시 추가적인 검토를 권장합니다.
{'='*50}
"""
        
        return body.strip()

# 전역 이메일 서비스 인스턴스
email_service = EmailService()
