import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { analysisService } from '../services';

const Feedback = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [feedback, setFeedback] = useState(null);
  const [loading, setLoading] = useState(true);
  const [problemNumber, setProblemNumber] = useState('');
  const [showAICode, setShowAICode] = useState(false);
  const [aiCode, setAiCode] = useState(null);
  const [loadingAICode, setLoadingAICode] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (location.state?.submissionId && location.state?.problemNumber) {
      setProblemNumber(location.state.problemNumber);
      fetchAnalysisResult(location.state.submissionId);
    } else {
      setLoading(false);
    }
  }, [location.state]);

  const fetchAnalysisResult = async (submissionId) => {
    try {
      setLoading(true);
      setError(null);
      const response = await analysisService.analyzeSubmittedCode(submissionId);

      if (response.status === 'success' && response.data) {
        const data = response.data;
        setFeedback({
          title: `문제 ${problemNumber}번 피드백`,
          score: data.score,
          strengths: data.strengths ? data.strengths.split('\n').filter(s => s.trim()) : ['코드가 정상적으로 작동합니다'],
          improvements: data.improvements ? data.improvements.split('\n').filter(s => s.trim()) : ['더 효율적인 방법을 고려해보세요'],
          suggestions: data.core_concept ? [data.core_concept] : ['다양한 방법으로 문제를 접근해보세요'],
          timeComplexity: {
            analysis: data.time_complexity || 'O(n)',
            description: `${data.algorithm_type || '구현'} 알고리즘을 사용한 솔루션입니다.`,
            efficiency: data.score >= 80 ? '우수' : data.score >= 60 ? '보통' : '개선 필요',
            color: data.score >= 80 ? 'green' : data.score >= 60 ? 'yellow' : 'red'
          },
          code: data.submitted_code || '// 코드를 불러올 수 없습니다',
          aiCode: null
        });
      }
    } catch (error) {
      console.error('Failed to fetch analysis result:', error);
      setError('분석 결과를 불러올 수 없습니다.');
    } finally {
      setLoading(false);
    }
  };

  const fetchAICode = async () => {
    if (!feedback) return;

    try {
      setLoadingAICode(true);
      const response = await analysisService.getOptimizedCode({
        problem_id: parseInt(problemNumber),
        language: 'python', // 기본 언어
        current_code: feedback.code
      });

      if (response.status === 'success' && response.data) {
        setAiCode({
          code: response.data.optimized_code,
          explanation: response.data.explanation,
          insights: response.data.key_insights || []
        });
      }
    } catch (error) {
      console.error('Failed to fetch AI optimized code:', error);
      setAiCode({
        code: '// AI 최적화 코드를 불러올 수 없습니다',
        explanation: '현재 AI 최적화 서비스를 이용할 수 없습니다.',
        insights: []
      });
    } finally {
      setLoadingAICode(false);
    }
  };

  const handleShowAICode = () => {
    setShowAICode(true);
    if (!aiCode) {
      fetchAICode();
    }
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

  if (error) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">오류가 발생했습니다</h1>
          <p className="text-red-600 mb-8">{error}</p>
          <div className="space-x-4">
            <button
              onClick={() => navigate('/guide')}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              문제 가이드로 이동
            </button>
            <button
              onClick={() => navigate('/')}
              className="px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
            >
              메인으로 돌아가기
            </button>
          </div>
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
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8 relative">
        <div className="flex items-center space-x-3">
          <img
            src="/images/푸앙_의복기본.png"
            alt="푸앙"
            className="w-12 h-12 object-contain"
          />
          <h1 className="text-3xl font-bold text-[#143365] mb-2">{feedback.title}</h1>
        </div>
        <img
          src="/images/푸앙_사랑.png"
          alt="푸앙"
          className="w-16 h-16 object-contain absolute top-0 right-0 opacity-30"
        />
      </div>
      <div className="mb-8">
        <div className="flex items-center space-x-4">
          <div className="flex items-center">
            <span className="text-lg font-medium text-gray-700 mr-2">점수</span>
            <span className="text-2xl font-bold text-[#2B95C3]">{feedback.score}</span>
            <span className="text-gray-500 ml-1">/100</span>
          </div>
          <div className="flex-1 bg-gray-200 rounded-full h-2">
            <div
              className="bg-[#2B95C3] h-2 rounded-full transition-all duration-500"
              style={{ width: `${feedback.score}%` }}
            ></div>
          </div>
        </div>
      </div>

      {/* 제출한 코드 */}
      <div className="mb-8">
        <div className="bg-gray-50 rounded-xl p-6 border">
          <h3 className="text-lg font-semibold text-[#143365] mb-4">제출한 코드</h3>
          <div className="bg-gray-800 rounded-lg p-4 overflow-x-auto">
            <pre className="text-gray-100 text-sm">
              <code>{feedback.code}</code>
            </pre>
          </div>
        </div>
      </div>

      {/* AI 코드 보기 모달 */}
      {showAICode && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-semibold text-[#143365]">AI가 제안하는 최적 코드</h3>
                <button
                  onClick={() => setShowAICode(false)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  ✕
                </button>
              </div>

              {loadingAICode ? (
                <div className="text-center py-8">
                  <div className="w-8 h-8 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin mx-auto mb-4"></div>
                  <p className="text-gray-600">AI가 최적화된 코드를 생성하고 있습니다...</p>
                </div>
              ) : aiCode ? (
                <>
                  <div className="bg-gray-800 rounded-lg p-4 overflow-x-auto">
                    <pre className="text-gray-100 text-sm">
                      <code>{aiCode.code}</code>
                    </pre>
                  </div>
                  <div className="mt-4 p-4 bg-blue-50 rounded-lg">
                    <h4 className="font-medium text-blue-900 mb-2">💡 AI 코드 설명</h4>
                    <p className="text-sm text-blue-700">
                      {aiCode.explanation || '이 코드는 더 효율적인 알고리즘과 최적화 기법을 적용한 버전입니다.'}
                    </p>
                    {aiCode.insights && aiCode.insights.length > 0 && (
                      <div className="mt-3">
                        <h5 className="font-medium text-blue-900 mb-1">핵심 개선 사항:</h5>
                        <ul className="text-sm text-blue-700 list-disc list-inside">
                          {aiCode.insights.map((insight, index) => (
                            <li key={index}>{insight}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </>
              ) : (
                <div className="text-center py-8">
                  <p className="text-gray-600">AI 코드를 불러올 수 없습니다.</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* 4가지 피드백 사항 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
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

        <div className={`bg-${feedback.timeComplexity.color}-50 rounded-xl p-6 border border-${feedback.timeComplexity.color}-200`}>
          <h3 className={`text-lg font-semibold text-${feedback.timeComplexity.color}-800 mb-4`}>🕒 시간 복잡도</h3>
          <div className="space-y-3">
            <div className="flex items-center space-x-2">
              <span className={`text-2xl font-bold text-${feedback.timeComplexity.color}-600`}>
                {feedback.timeComplexity.analysis}
              </span>
              <span className={`px-2 py-1 text-xs rounded-full bg-${feedback.timeComplexity.color}-100 text-${feedback.timeComplexity.color}-700`}>
                {feedback.timeComplexity.efficiency}
              </span>
            </div>
            <p className={`text-${feedback.timeComplexity.color}-700 text-sm`}>
              {feedback.timeComplexity.description}
            </p>
          </div>
        </div>
      </div>

      {/* 버튼 */}
      <div className="flex flex-col sm:flex-row justify-center space-y-3 sm:space-y-0 sm:space-x-4">
        <button
          onClick={handleRetry}
          className="px-8 py-3 bg-[#2B95C3] text-white rounded-lg hover:bg-[#143365] transition-colors font-medium"
        >
          다시 풀어보기
        </button>
        <button
          onClick={() => navigate('/')}
          className="px-8 py-3 bg-[#143365] text-white rounded-lg hover:bg-[#2B95C3] transition-colors font-medium"
        >
          메인으로 돌아가기
        </button>
        <button
          onClick={handleShowAICode}
          className="px-8 py-3 bg-[#DEACC5] text-white rounded-lg hover:bg-[#D7BCA1] transition-colors font-medium"
        >
          AI 코드 보기
        </button>
      </div>
    </div>
  );
};

export default Feedback;