import React from 'react';

const Help = () => {
  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="bg-white rounded-xl shadow-sm border p-8">
        <h1 className="text-3xl font-bold text-[#143365] mb-6">도움말</h1>
        <div className="prose max-w-none">
          <p className="text-gray-700 text-lg leading-relaxed">
            도움말 페이지입니다.
          </p>
          <div className="mt-8 p-6 bg-blue-50 rounded-lg border border-blue-200">
            <p className="text-[#2B95C3] font-medium">
              CAU Code 사용 중 궁금한 점이 있으시면 FAQ 페이지를 참고하거나 문의하기를 통해 연락주세요.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Help;