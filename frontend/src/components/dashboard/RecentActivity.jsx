import React, { useState, useEffect } from 'react';
import { userService } from '../../services';

const RecentActivity = () => {
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchRecentActivities();
  }, []);

  const fetchRecentActivities = async () => {
    try {
      setLoading(true);
      const response = await userService.getRecentActivities();

      if (response.status === 'success' && response.data?.activities) {
        const formattedActivities = response.data.activities.map(activity => ({
          time: formatTime(activity.timestamp),
          description: formatDescription(activity),
          color: getActivityColor(activity.type)
        }));
        setActivities(formattedActivities);
      } else {
        // API에서 데이터가 없으면 빈 배열로 설정
        setActivities([]);
      }
    } catch (error) {
      console.error('Failed to fetch recent activities:', error);
      setActivities([]);
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (timestamp) => {
    if (!timestamp) return '방금 전';
    const now = new Date();
    const activityTime = new Date(timestamp);
    const diffInHours = Math.floor((now - activityTime) / (1000 * 60 * 60));

    if (diffInHours < 1) return '방금 전';
    if (diffInHours < 24) return `${diffInHours}시간 전`;
    return `${Math.floor(diffInHours / 24)}일 전`;
  };

  const formatDescription = (activity) => {
    if (activity.type === 'problem_solved') {
      return `[${activity.problem_id}] ${activity.problem_title || '문제'} 해결완료`;
    } else if (activity.type === 'feedback_request') {
      return `[${activity.problem_id}] ${activity.problem_title || '문제'} 피드백 요청`;
    }
    return activity.description || '활동 내역';
  };

  const getActivityColor = (type) => {
    switch (type) {
      case 'problem_solved': return 'bg-green-500';
      case 'feedback_request': return 'bg-purple-500';
      default: return 'bg-gray-500';
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">최근 활동</h3>
      <div className="space-y-3">
        {loading ? (
          Array.from({ length: 3 }).map((_, index) => (
            <div key={index} className="flex items-center space-x-3 text-sm animate-pulse">
              <div className="w-2 h-2 bg-gray-200 rounded-full"></div>
              <div className="h-3 bg-gray-200 rounded w-16"></div>
              <div className="h-3 bg-gray-200 rounded w-32"></div>
            </div>
          ))
        ) : activities.length > 0 ? (
          activities.map((activity, index) => (
            <div key={index} className="flex items-center space-x-3 text-sm">
              <div className={`w-2 h-2 ${activity.color} rounded-full`}></div>
              <span className="text-gray-600">{activity.time}</span>
              <span className="font-medium">{activity.description}</span>
            </div>
          ))
        ) : (
          <div className="text-center py-4 text-gray-500">
            <p>최근 활동이 없습니다.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default RecentActivity;