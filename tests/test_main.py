"""
메인 모듈에 대한 테스트
"""

import unittest
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import main


class TestMain(unittest.TestCase):
    """메인 모듈 테스트 클래스"""
    
    def test_main_function_exists(self):
        """main 함수가 존재하는지 테스트"""
        self.assertTrue(callable(main))
    
    def test_main_function_returns_none(self):
        """main 함수가 None을 반환하는지 테스트"""
        result = main()
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main() 