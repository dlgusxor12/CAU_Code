import React from 'react';

const FeatureRequest = () => {
  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="bg-white rounded-xl shadow-sm border p-8">
        <h1 className="text-3xl font-bold text-[#143365] mb-6">기능 제안</h1>
        <div className="prose max-w-none">
          <p className="text-gray-700 text-lg leading-relaxed">
            기능 제안 페이지입니다.
          </p>
          <div className="mt-8 p-6 bg-blue-50 rounded-lg border border-blue-200">
            <p className="text-[#2B95C3] font-medium">
              CAU Code를 더 좋은 서비스로 만들기 위한 여러분의 의견을 기다립니다.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FeatureRequest;