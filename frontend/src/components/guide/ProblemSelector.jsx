import React from 'react';

const ProblemSelector = ({ problemNumber, setProblemNumber, isReadOnly = false }) => {
  const handleProblemChange = (e) => {
    if (!isReadOnly) {
      setProblemNumber(e.target.value);
    }
  };

  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-2">문제 번호</label>
      <input 
        type="text" 
        value={problemNumber}
        onChange={handleProblemChange}
        placeholder="예: 1000" 
        readOnly={isReadOnly}
        className={`w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
          isReadOnly ? 'bg-gray-100 cursor-not-allowed' : ''
        }`}
      />
      {problemNumber && (
        <p className="text-xs text-gray-500 mt-1">
          백준 온라인 저지 {problemNumber}번 문제
        </p>
      )}
    </div>
  );
};

export default ProblemSelector;