import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

const Feedback = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [feedback, setFeedback] = useState(null);
  const [loading, setLoading] = useState(true);
  const [problemNumber, setProblemNumber] = useState('');

  useEffect(() => {
    if (location.state?.problemNumber) {
      setProblemNumber(location.state.problemNumber);
      setTimeout(() => {
        setFeedback(generateMockFeedback(location.state.problemNumber));
        setLoading(false);
      }, 1500);
    } else {
      setLoading(false);
    }
  }, [location.state]);

  const generateMockFeedback = (problemNum) => {
    const feedbacks = {
      '1000': {
        title: 'A+B 문제 피드백',
        score: 85,
        strengths: [
          '입출력 처리가 정확합니다',
          '코드 구조가 깔끔합니다',
          '변수명이 명확합니다'
        ],
        improvements: [
          '예외 처리를 추가하면 더 좋겠습니다',
          '주석을 추가하여 가독성을 높일 수 있습니다'
        ],
        suggestions: [
          '더 복잡한 수학 문제에 도전해보세요',
          '입출력 최적화 방법을 학습해보세요'
        ],
        code: `#include <iostream>
using namespace std;

int main() {
    int A, B;
    cin >> A >> B;
    cout << A + B << endl;
    return 0;
}`
      }
    };

    return feedbacks[problemNum] || {
      title: `문제 ${problemNum}번 피드백`,
      score: 78,
      strengths: ['코드가 동작합니다'],
      improvements: ['더 나은 알고리즘을 고려해보세요'],
      suggestions: ['다양한 방법으로 문제를 접근해보세요'],
      code: '// 코드 분석 중...'
    };
  };

  const handleRetry = () => {
    navigate('/guide', { 
      state: { 
        problemId: problemNumber,
        isRetry: true 
      } 
    });
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin mx-auto mb-4"></div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">AI가 코드를 분석하고 있습니다...</h2>
          <p className="text-gray-600">잠시만 기다려주세요</p>
        </div>
      </div>
    );
  }

  if (!feedback) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">코드 피드백</h1>
          <p className="text-gray-600 mb-8">문제 가이드에서 코드를 제출하면 AI 피드백을 받을 수 있습니다</p>
          <button 
            onClick={() => navigate('/guide')}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            문제 가이드로 이동
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">{feedback.title}</h1>
        <div className="flex items-center space-x-4">
          <div className="flex items-center">
            <span className="text-2xl font-bold text-blue-600">{feedback.score}</span>
            <span className="text-gray-500 ml-1">/100</span>
          </div>
          <div className="flex-1 bg-gray-200 rounded-full h-2">
            <div 
              className="bg-blue-600 h-2 rounded-full transition-all duration-500"
              style={{ width: `${feedback.score}%` }}
            ></div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="space-y-6">
          <div className="bg-green-50 rounded-xl p-6 border border-green-200">
            <h3 className="text-lg font-semibold text-green-800 mb-4">✓ 잘한 점</h3>
            <ul className="space-y-2">
              {feedback.strengths.map((strength, index) => (
                <li key={index} className="text-green-700">• {strength}</li>
              ))}
            </ul>
          </div>

          <div className="bg-yellow-50 rounded-xl p-6 border border-yellow-200">
            <h3 className="text-lg font-semibold text-yellow-800 mb-4">⚠ 개선 사항</h3>
            <ul className="space-y-2">
              {feedback.improvements.map((improvement, index) => (
                <li key={index} className="text-yellow-700">• {improvement}</li>
              ))}
            </ul>
          </div>

          <div className="bg-blue-50 rounded-xl p-6 border border-blue-200">
            <h3 className="text-lg font-semibold text-blue-800 mb-4">★ 추천 사항</h3>
            <ul className="space-y-2">
              {feedback.suggestions.map((suggestion, index) => (
                <li key={index} className="text-blue-700">• {suggestion}</li>
              ))}
            </ul>
          </div>
        </div>

        <div className="space-y-6">
          <div className="bg-gray-50 rounded-xl p-6 border">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">제출한 코드</h3>
            <div className="bg-gray-800 rounded-lg p-4 overflow-x-auto">
              <pre className="text-gray-100 text-sm">
                <code>{feedback.code}</code>
              </pre>
            </div>
          </div>

          <div className="space-y-3">
            <button 
              onClick={handleRetry}
              className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              다시 풀어보기
            </button>
            <button 
              onClick={() => navigate('/problems')}
              className="w-full px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium"
            >
              다른 문제 도전하기
            </button>
            <button 
              onClick={() => navigate('/')}
              className="w-full px-6 py-2 text-gray-600 hover:text-gray-800 transition-colors"
            >
              메인으로 돌아가기
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Feedback;