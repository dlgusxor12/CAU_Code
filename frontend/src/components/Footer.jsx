import React from 'react';

const Footer = () => {
  return (
    <footer className="bg-gray-900 text-white mt-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* 회사 정보 */}
          <div className="col-span-1 md:col-span-2">
            <div className="flex items-center space-x-3 mb-4">
              <h3 className="text-2xl font-bold text-blue-400">CAU Code</h3>
            </div>
            <p className="text-gray-300 mb-4 leading-relaxed">
              중앙대학교 학생들을 위한 알고리즘 문제 추천 및 코드 리뷰 서비스입니다. 
              AI 기반 개인 맞춤형 문제 추천으로 효율적인 알고리즘 학습을 지원합니다.
            </p>
            
          </div>
          
          {/* 서비스 */}
          <div>
            <h4 className="text-lg font-semibold mb-4">서비스</h4>
            <ul className="space-y-2">
              <li><a href="/problems" className="text-gray-300 hover:text-white transition-colors">문제 추천</a></li>
              <li><a href="/guide" className="text-gray-300 hover:text-white transition-colors">학습 가이드</a></li>
              <li><a href="/ranking" className="text-gray-300 hover:text-white transition-colors">랭킹 시스템</a></li>
              <li><span className="text-gray-500 cursor-not-allowed">진도 관리</span></li>
            </ul>
          </div>
          
          {/* 지원 */}
          <div>
            <h4 className="text-lg font-semibold mb-4">지원</h4>
            <ul className="space-y-2">
              <li><a href="#" className="text-gray-300 hover:text-white transition-colors">도움말</a></li>
              <li><a href="#" className="text-gray-300 hover:text-white transition-colors">FAQ</a></li>
              <li><a href="#" className="text-gray-300 hover:text-white transition-colors">문의하기</a></li>
              <li><a href="#" className="text-gray-300 hover:text-white transition-colors">버그 신고</a></li>
              <li><a href="#" className="text-gray-300 hover:text-white transition-colors">기능 제안</a></li>
            </ul>
          </div>
        </div>
        
        {/* 하단 구분선 및 저작권 */}
        <div className="border-t border-gray-700 mt-8 pt-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex flex-wrap justify-center md:justify-start space-x-6 mb-4 md:mb-0">
              <a href="#" className="text-gray-300 hover:text-white text-sm transition-colors">개인정보처리방침</a>
              <a href="#" className="text-gray-300 hover:text-white text-sm transition-colors">이용약관</a>
              <a href="#" className="text-gray-300 hover:text-white text-sm transition-colors">사이트 소개</a>
              <a href="#" className="text-gray-300 hover:text-white text-sm transition-colors">공지사항</a>
              <a href="#" className="text-gray-300 hover:text-white text-sm transition-colors">채용정보</a>
            </div>
            <div className="text-gray-400 text-sm text-center md:text-right">
              <p>&copy; 2025 CAU Code. All rights reserved.</p>
              <p className="mt-1">중앙대학교 소프트웨어학부</p>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;