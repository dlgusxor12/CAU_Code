import React from 'react';
import { useNavigate } from 'react-router-dom';

const QuickActions = () => {
  const navigate = useNavigate();

  const actions = [
    {
      title: '문제 요청하기',
      icon: (
        <img
          src="/images/푸앙_집중.png"
          alt="푸앙"
          className="w-8 h-8 object-contain"
        />
      ),
      gradient: 'bg-gradient-to-br from-[#2B95C3] to-[#3DB1D3] hover:from-[#143365] hover:to-[#2B95C3]',
      onClick: () => navigate('/problems')
    },
    {
      title: '문제 가이드',
      icon: (
        <img
          src="/images/푸앙_독서.png"
          alt="푸앙"
          className="w-8 h-8 object-contain"
        />
      ),
      gradient: 'bg-gradient-to-br from-[#DEACC5] to-[#F2D6E3] hover:from-[#D7BCA1] hover:to-[#DEACC5]',
      onClick: () => navigate('/guide')
    }
  ];

  return (
    <div className="bg-white rounded-xl shadow-sm border p-6">
      <h3 className="text-lg font-semibold text-[#143365] mb-4">빠른 실행</h3>
      <div className="grid grid-cols-2 gap-3">
        {actions.map((action, index) => (
          <button
            key={index}
            onClick={action.onClick}
            className={`p-4 ${action.gradient} text-white rounded-lg transition-all hover:shadow-md hover:scale-105 text-center`}
          >
            <div className="flex flex-col items-center space-y-2">
              {action.icon}
              <span className="font-medium text-sm">{action.title}</span>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
};

export default QuickActions;