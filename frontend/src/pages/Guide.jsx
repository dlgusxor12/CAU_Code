import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import ProblemSelector from '../components/guide/ProblemSelector';
import LanguageSelector from '../components/guide/LanguageSelector';
import CodeEditor from '../components/guide/CodeEditor';
import SubmissionModal from '../components/guide/SubmissionModal';
import ProblemInfo from '../components/guide/ProblemInfo';

const Guide = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [problemNumber, setProblemNumber] = useState('');
  const [language, setLanguage] = useState('');
  const [code, setCode] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [submissionType, setSubmissionType] = useState(''); // 'feedback' or 'solve'
  const [isReadOnly, setIsReadOnly] = useState(false);
  const [alertModal, setAlertModal] = useState({ isOpen: false, message: '' });

  useEffect(() => {
    // URL state에서 문제 정보 가져오기
    if (location.state?.problemId) {
      setProblemNumber(location.state.problemId.toString());
      setIsReadOnly(true);
    }

    // 피드백 페이지에서 온 경우 이전 코드 설정
    if (location.state?.previousCode && location.state?.isRetry) {
      setCode(location.state.previousCode);
    }
  }, [location.state]);

  const handleSubmit = (type) => {
    const missingFields = [];

    if (!problemNumber) missingFields.push('문제 번호');
    if (!language) missingFields.push('언어 선택');
    if (!code.trim()) missingFields.push('코드 입력');

    if (missingFields.length > 0) {
      const message = missingFields.length === 1
        ? `${missingFields[0]}을 완료해주세요.`
        : `${missingFields.join(', ')}을 완료해주세요.`;
      setAlertModal({ isOpen: true, message });
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
    return '해결 완료';
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8 relative">
        <div className="flex items-center space-x-3">
          <img
            src="/images/푸앙_독서.png"
            alt="푸앙"
            className="w-12 h-12 object-contain"
          />
          <div>
            <h1 className="text-3xl font-bold text-[#143365] mb-2">문제 가이드</h1>
            <p className="text-[#2B95C3]">코드를 제출하고 피드백을 받아보세요</p>
          </div>
        </div>
        <img
          src="/images/푸앙_집중.png"
          alt="푸앙"
          className="w-16 h-16 object-contain absolute top-0 right-0 opacity-30"
        />
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
            className="px-8 py-3 bg-[#2B95C3] text-white font-medium rounded-lg hover:bg-[#143365] transition-colors focus:outline-none focus:ring-2 focus:ring-[#6BBEE2] focus:ring-offset-2"
          >
            피드백 받기
          </button>
          <button
            onClick={() => handleSubmit('solve')}
            className="px-8 py-3 bg-[#DEACC5] text-white font-medium rounded-lg hover:bg-[#D7BCA1] transition-colors focus:outline-none focus:ring-2 focus:ring-[#F2D6E3] focus:ring-offset-2"
          >
            {getButtonText()}
          </button>
          <button
            onClick={() => navigate('/')}
            className="px-8 py-3 bg-[#143365] text-white font-medium rounded-lg hover:bg-[#2B95C3] transition-colors focus:outline-none focus:ring-2 focus:ring-[#6BBEE2] focus:ring-offset-2"
          >
            메인으로 돌아가기
          </button>
        </div>

        {/* 도움말 */}
        <div className="mt-8 p-4 bg-blue-50 rounded-lg relative">
          <img
            src="/images/푸앙_어푸앙.png"
            alt="푸앙"
            className="w-8 h-8 object-contain absolute top-4 right-4 opacity-60"
          />
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
        language={language}
        code={code}
      />

      {/* 알림 모달 */}
      {alertModal.isOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl p-6 max-w-md w-full shadow-lg">
            <div className="flex items-center mb-4">
              <img
                src="/images/푸앙_어푸앙.png"
                alt="푸앙"
                className="w-12 h-12 object-contain mr-3"
              />
              <h3 className="text-lg font-semibold text-gray-900">입력 확인</h3>
            </div>
            <p className="text-gray-600 mb-6">{alertModal.message}</p>
            <div className="flex justify-end">
              <button
                onClick={() => setAlertModal({ isOpen: false, message: '' })}
                className="px-6 py-2 bg-[#2B95C3] text-white rounded-lg hover:bg-[#143365] transition-colors font-medium"
              >
                확인
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Guide;