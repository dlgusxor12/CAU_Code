import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { guideService } from '../../services';

const SubmissionModal = ({ isOpen, onClose, submissionType, problemNumber, language, code }) => {
  const [status, setStatus] = useState('verifying'); // verifying, success, error
  const [message, setMessage] = useState('');
  const [submissionId, setSubmissionId] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (isOpen) {
      handleSubmission();
    }
  }, [isOpen, submissionType, problemNumber, language, code]);

  const handleSubmission = async () => {
    try {
      setStatus('verifying');
      setMessage(submissionType === 'feedback' ? '코드를 분석하고 있습니다...' : '코드를 검증하고 있습니다...');

      if (submissionType === 'feedback') {
        // 피드백을 위한 코드 제출
        const response = await guideService.submitCodeForAnalysis({
          problem_id: parseInt(problemNumber),
          language: language,
          code: code
        });

        if (response.status === 'success') {
          setSubmissionId(response.data.submission_id);
          setStatus('success');
          setMessage(`문제 ${problemNumber}번 코드 분석이 완료되었습니다.`);
        }
      } else {
        // 해결 완료를 위한 검증
        const verifyResponse = await guideService.verifySolution(parseInt(problemNumber));

        if (verifyResponse.status === 'success') {
          const isVerified = verifyResponse.data.is_solved;

          if (isVerified) {
            setStatus('success');
            setMessage(`문제 ${problemNumber}번이 성공적으로 해결되었습니다.`);
          } else {
            setStatus('error');
            setMessage('아직 이 문제를 해결하지 않았습니다. 백준에서 먼저 문제를 해결해주세요.');
          }
        }
      }
    } catch (error) {
      console.error('Submission error:', error);
      setStatus('error');
      setMessage('제출 중 오류가 발생했습니다. 다시 시도해주세요.');
    }
  };

  const handleClose = () => {
    onClose();
    if (submissionType === 'feedback' && submissionId) {
      navigate('/feedback', {
        state: {
          problemNumber,
          submissionId,
          fromGuide: true
        }
      });
    } else if (submissionType === 'solve') {
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

          {status === 'error' && (
            <>
              <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-red-600" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"/>
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                {submissionType === 'feedback' ? '분석 실패' : '검증 실패'}
              </h3>
            </>
          )}
          
          <p className="text-gray-600 mb-6">{message}</p>
          
          {(status === 'success' || status === 'error') && (
            <div className="space-y-3">
              {status === 'success' && (
                <button
                  onClick={handleClose}
                  className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
                >
                  {submissionType === 'feedback' ? '피드백 확인하기' : '메인으로 돌아가기'}
                </button>
              )}

              {status === 'error' && (
                <button
                  onClick={onClose}
                  className="w-full px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-medium"
                >
                  닫기
                </button>
              )}

              {submissionType === 'solve' && status === 'success' && (
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