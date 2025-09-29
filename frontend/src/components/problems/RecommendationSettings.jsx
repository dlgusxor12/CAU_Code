import React, { useState } from 'react';

const RecommendationSettings = ({ onSettingsChange }) => {
  const [settings, setSettings] = useState({
    recommendationType: 'adaptive', // adaptive, similar, challenge
    problemCount: 5,
    includeWrongProblems: true,
    focusWeakAreas: true
  });

  const handleSettingChange = (key, value) => {
    const newSettings = { ...settings, [key]: value };
    setSettings(newSettings);
    onSettingsChange(newSettings);
  };

  const recommendationTypes = [
    {
      value: 'ai_recommendation',
      label: 'AI 추천',
      description: 'AI가 당신의 실력에 맞는 문제를 추천합니다'
    },
    {
      value: 'appropriate_difficulty',
      label: '적정 난이도',
      description: '현재 티어에 적합한 난이도의 문제를 추천합니다'
    },
    { 
      value: 'challenge', 
      label: '도전 모드', 
      description: '현재 레벨보다 약간 어려운 문제를 추천합니다' 
    }
  ];

  return (
    <div className="bg-white rounded-xl shadow-sm border p-6 mb-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-6">추천 설정</h3>
      
      <div className="space-y-6">
        {/* 추천 방식 선택 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">추천 방식</label>
          <div className="grid grid-cols-1 gap-3">
            {recommendationTypes.map((type) => (
              <label key={type.value} className="flex items-start space-x-3 cursor-pointer">
                <input
                  type="radio"
                  name="recommendationType"
                  value={type.value}
                  checked={settings.recommendationType === type.value}
                  onChange={(e) => handleSettingChange('recommendationType', e.target.value)}
                  className="mt-1 text-blue-600 focus:ring-blue-500"
                />
                <div>
                  <div className="font-medium text-gray-900">{type.label}</div>
                  <div className="text-sm text-gray-600">{type.description}</div>
                </div>
              </label>
            ))}
          </div>
        </div>

        {/* 문제 개수 설정 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            추천 문제 개수: {settings.problemCount}개
          </label>
          <input
            type="range"
            min="1"
            max="10"
            value={settings.problemCount}
            onChange={(e) => handleSettingChange('problemCount', parseInt(e.target.value))}
            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
          />
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>1개</span>
            <span>10개</span>
          </div>
        </div>


        {/* 추천 받기 버튼 */}
        <button 
          onClick={() => onSettingsChange(settings, true)}
          className="w-full px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
        >
          새로운 문제 추천받기
        </button>
      </div>
    </div>
  );
};

export default RecommendationSettings;