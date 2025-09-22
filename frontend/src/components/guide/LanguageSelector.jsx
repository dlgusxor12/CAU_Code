import React, { useState, useEffect } from 'react';
import { guideService } from '../../services';

const LanguageSelector = ({ language, setLanguage }) => {
  const [languages, setLanguages] = useState([
    { language: '', display_name: '언어를 선택하세요' }
  ]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSupportedLanguages();
  }, []);

  const fetchSupportedLanguages = async () => {
    try {
      setLoading(true);
      const response = await guideService.getSupportedLanguages();

      if (response.status === 'success' && response.data) {
        const supportedLanguages = [
          { language: '', display_name: '언어를 선택하세요' },
          ...response.data.languages
        ];
        setLanguages(supportedLanguages);
      }
    } catch (error) {
      console.error('Failed to fetch supported languages:', error);
      // 실패 시 기본 언어 목록 사용
      setLanguages([
        { language: '', display_name: '언어를 선택하세요' },
        { language: 'python', display_name: 'Python 3' },
        { language: 'java', display_name: 'Java' },
        { language: 'cpp', display_name: 'C++' },
        { language: 'c', display_name: 'C' },
        { language: 'javascript', display_name: 'JavaScript' }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-2">언어 선택</label>
      <select
        value={language}
        onChange={(e) => setLanguage(e.target.value)}
        disabled={loading}
        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
      >
        {loading ? (
          <option value="">언어 목록을 불러오는 중...</option>
        ) : (
          languages.map((lang) => (
            <option key={lang.language} value={lang.language}>
              {lang.display_name}
            </option>
          ))
        )}
      </select>
    </div>
  );
};

export default LanguageSelector;