import React from 'react';

const LanguageSelector = ({ language, setLanguage }) => {
  const languages = [
    { value: '', label: '언어를 선택하세요' },
    { value: 'python', label: 'Python' },
    { value: 'java', label: 'Java' },
    { value: 'cpp', label: 'C++' },
    { value: 'c', label: 'C' },
    { value: 'javascript', label: 'JavaScript' },
    { value: 'go', label: 'Go' },
    { value: 'rust', label: 'Rust' }
  ];

  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-2">언어 선택</label>
      <select 
        value={language}
        onChange={(e) => setLanguage(e.target.value)}
        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
      >
        {languages.map((lang) => (
          <option key={lang.value} value={lang.value}>
            {lang.label}
          </option>
        ))}
      </select>
    </div>
  );
};

export default LanguageSelector;