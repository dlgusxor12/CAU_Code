import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const SubmissionModal = ({ isOpen, onClose, submissionType, problemNumber }) => {
  const [status, setStatus] = useState('verifying'); // verifying, success, error
  const [message, setMessage] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    if (isOpen) {
      setStatus('verifying');
      setMessage(submissionType === 'feedback' ? '코드를 분석하고 있습니다...' : '코드를 검증하고 있습니다...');
      
      // 2초 후 완료 시뮬레이션
      const timer = setTimeout(() => {
        setStatus('success');
        setMessage(
          submissionType === 'feedback' 
            ? `문제 ${problemNumber}번 코드 분석이 완료되었습니다.` 
            : `문제 ${problemNumber}번이 성공적으로 해결되었습니다.`
        );
      }, 2000);

      return () => clearTimeout(timer);
    }
  }, [isOpen, submissionType, problemNumber]);

  const handleClose = () => {
    onClose();
    if (submissionType === 'feedback') {
      navigate('/feedback', { 
        state: { 
          problemNumber,
          fromGuide: true 
        } 
      });
    } else {
      navigate('/');
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl p-8 max-w-md w-full mx-4">
        <div className="text-center">
          {status === 'verifying' && (
            <>
              <div className="w-16 h-16 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin mx-auto mb-4"></div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                {submissionType === 'feedback' ? '분석 중입니다...' : '검증 중입니다...'}
              </h3>
            </>
          )}
          
          {status === 'success' && (
            <>
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"/>
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                {submissionType === 'feedback' ? '분석 완료!' : '검증 완료!'}
              </h3>
            </>
          )}
          
          <p className="text-gray-600 mb-6">{message}</p>
          
          {status === 'success' && (
            <div className="space-y-3">
              <button 
                onClick={handleClose}
                className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
              >
                {submissionType === 'feedback' ? '피드백 확인하기' : '메인으로 돌아가기'}
              </button>
              
              {submissionType === 'solve' && (
                <button 
                  onClick={onClose}
                  className="w-full px-6 py-2 text-gray-600 hover:text-gray-800 transition-colors"
                >
                  계속 문제 풀기
                </button>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SubmissionModal;