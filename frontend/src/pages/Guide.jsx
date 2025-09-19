import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import ProblemSelector from '../components/guide/ProblemSelector';
import LanguageSelector from '../components/guide/LanguageSelector';
import CodeEditor from '../components/guide/CodeEditor';
import SubmissionModal from '../components/guide/SubmissionModal';
import ProblemInfo from '../components/guide/ProblemInfo';

const Guide = () => {
  const location = useLocation();
  const [problemNumber, setProblemNumber] = useState('');
  const [language, setLanguage] = useState('');
  const [code, setCode] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [submissionType, setSubmissionType] = useState(''); // 'feedback' or 'solve'
  const [isReadOnly, setIsReadOnly] = useState(false);

  useEffect(() => {
    // URL state에서 문제 정보 가져오기
    if (location.state?.problemId) {
      setProblemNumber(location.state.problemId.toString());
      setIsReadOnly(true);
    }
  }, [location.state]);

  const handleSubmit = (type) => {
    if (!problemNumber || !language || !code.trim()) {
      alert('모든 필드를 입력해주세요.');
      return;
    }
    
    setSubmissionType(type);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    
    // 모달 상태 초기화
    setTimeout(() => {
      setSubmissionType('');
    }, 300);
  };

  const getButtonText = () => {
    if (isReadOnly && location.state?.isRetry) {
      return '다시 풀기';
    }
    return '해결 완료';
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">문제 가이드</h1>
        <p className="text-gray-600">코드를 제출하고 피드백을 받아보세요</p>
      </div>

      {/* 문제 정보 표시 */}
      {problemNumber && <ProblemInfo problemNumber={problemNumber} />}

      <div className="bg-white rounded-xl shadow-sm border p-6">
        {/* 윗 부분: 문제 번호와 언어 선택 */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <ProblemSelector 
            problemNumber={problemNumber}
            setProblemNumber={setProblemNumber}
            isReadOnly={isReadOnly}
          />
          <LanguageSelector 
            language={language}
            setLanguage={setLanguage}
          />
        </div>
        
        {/* 중간 부분: 코드 입력 영역 */}
        <div className="mb-6">
          <CodeEditor 
            code={code}
            setCode={setCode}
            language={language}
          />
        </div>
        
        {/* 아래 부분: 버튼들 */}
        <div className="flex flex-col sm:flex-row justify-center space-y-3 sm:space-y-0 sm:space-x-4">
          <button 
            onClick={() => handleSubmit('feedback')}
            className="px-8 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            disabled={!problemNumber || !language || !code.trim()}
          >
            피드백 받기
          </button>
          <button 
            onClick={() => handleSubmit('solve')}
            className="px-8 py-3 bg-green-600 text-white font-medium rounded-lg hover:bg-green-700 transition-colors focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
            disabled={!problemNumber || !language || !code.trim()}
          >
            {getButtonText()}
          </button>
        </div>

        {/* 도움말 */}
        <div className="mt-8 p-4 bg-blue-50 rounded-lg">
          <h4 className="font-medium text-blue-900 mb-2">💡 사용 가이드</h4>
          <ul className="text-sm text-blue-700 space-y-1">
            <li>• <strong>피드백 받기:</strong> AI가 코드를 분석하여 개선점과 최적화 방안을 제안합니다</li>
            <li>• <strong>해결 완료:</strong> 문제를 완전히 해결했다고 판단되면 클릭하세요</li>
            <li>• 코드는 자동 저장되지 않으니 중요한 코드는 별도로 저장해두세요</li>
          </ul>
        </div>

        {/* 최근 제출 기록 */}
        <div className="mt-6 pt-6 border-t">
          <h4 className="font-medium text-gray-900 mb-3">최근 제출 기록</h4>
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm p-3 bg-green-50 rounded-lg">
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span>문제 1931번 - 회의실 배정</span>
                <span className="text-green-600 font-medium">통과</span>
              </div>
              <span className="text-gray-500">2시간 전</span>
            </div>
            <div className="flex items-center justify-between text-sm p-3 bg-red-50 rounded-lg">
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                <span>문제 1463번 - 1로 만들기</span>
                <span className="text-red-600 font-medium">실패</span>
              </div>
              <span className="text-gray-500">어제</span>
            </div>
          </div>
        </div>
      </div>

      {/* 제출 모달 */}
      <SubmissionModal 
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        submissionType={submissionType}
        problemNumber={problemNumber}
      />
    </div>
  );
};

export default Guide;