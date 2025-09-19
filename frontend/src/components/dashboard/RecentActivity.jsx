import React from 'react';

const RecentActivity = () => {
  const activities = [
    {
      time: '2시간 전',
      description: '[1931] 회의실 배정 해결',
      color: 'bg-green-500'
    },
    {
      time: '5시간 전',
      description: '코드 피드백 받음',
      color: 'bg-blue-500'
    },
    {
      time: '어제',
      description: '[11047] 동전 0 해결',
      color: 'bg-yellow-500'
    }
  ];

  return (
    <div className="bg-white rounded-xl shadow-sm border p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">최근 활동</h3>
      <div className="space-y-3">
        {activities.map((activity, index) => (
          <div key={index} className="flex items-center space-x-3 text-sm">
            <div className={`w-2 h-2 ${activity.color} rounded-full`}></div>
            <span className="text-gray-600">{activity.time}</span>
            <span className="font-medium">{activity.description}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default RecentActivity;