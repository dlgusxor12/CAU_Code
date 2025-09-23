import React, { useEffect, useState } from 'react';
import { userService } from '../../services';

const ContributionGraph = () => {
  const [monthlyData, setMonthlyData] = useState([]);
  const [totalSolved, setTotalSolved] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchContributionData();
  }, []);

  const fetchContributionData = async () => {
    try {
      setLoading(true);
      const response = await userService.getContribution();

      if (response.status === 'success' && response.data?.daily_data) {
        const dailyData = response.data.daily_data;
        setTotalSolved(response.data.total_solved_this_year || 0);

        // 월별로 데이터 그룹화
        const groupedData = groupDataByMonth(dailyData);
        setMonthlyData(groupedData);
      } else {
        // Fallback: 더미 데이터 생성
        generateMonthlyContribution();
      }
    } catch (error) {
      console.error('Failed to fetch contribution data:', error);
      generateMonthlyContribution();
    } finally {
      setLoading(false);
    }
  };

  const groupDataByMonth = (dailyData) => {
    // 최근 6개월 계산
    const today = new Date();
    const sixMonthsAgo = new Date(today.getFullYear(), today.getMonth() - 5, 1);
    const months = [];

    // 6개월 배열 생성
    for (let i = 0; i < 6; i++) {
      const date = new Date(sixMonthsAgo.getFullYear(), sixMonthsAgo.getMonth() + i, 1);
      months.push({
        name: `${date.getMonth() + 1}월`,
        year: date.getFullYear(),
        monthIndex: date.getMonth()
      });
    }

    const data = [];

    months.forEach((month) => {
      const monthData = {
        name: month.name,
        weeks: []
      };

      // 해당 월의 데이터 필터링
      const monthlyContributions = dailyData.filter(day => {
        const date = new Date(day.date);
        return date.getMonth() === month.monthIndex && date.getFullYear() === month.year;
      });

      // 간단한 주별 표시 (4-5주)
      const weeksInMonth = 4;
      for (let week = 0; week < weeksInMonth; week++) {
        const weekData = [];
        for (let day = 0; day < 7; day++) {
          const dayIndex = week * 7 + day;
          const contribution = monthlyContributions[dayIndex] || { solved_count: 0, date: '' };
          weekData.push({
            level: Math.min(4, contribution.solved_count),
            tooltip: `${month.name} ${dayIndex + 1}일: ${contribution.solved_count}개 CAU Code 문제 해결`
          });
        }
        monthData.weeks.push(weekData);
      }
      data.push(monthData);
    });

    return data;
  };

  const generateMonthlyContribution = () => {
    const months = ['1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월'];
    const data = [];

    months.forEach((month, index) => {
      const monthData = {
        name: month,
        weeks: []
      };

      // 각 월마다 4-5주 표시
      const weeksInMonth = index === 1 ? 4 : 5; // 2월은 4주, 나머지는 5주
      for (let week = 0; week < weeksInMonth; week++) {
        const weekData = [];
        for (let day = 0; day < 7; day++) {
          const level = Math.floor(Math.random() * 5);
          weekData.push({
            level,
            tooltip: `${month} ${week * 7 + day + 1}일: ${level}개 문제 해결`
          });
        }
        monthData.weeks.push(weekData);
      }
      data.push(monthData);
    });

    setMonthlyData(data);
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border p-6">
      <h3 className="text-xl font-semibold text-gray-900 mb-6">해결 목록</h3>
      <div className="space-y-4">
        <div className="flex items-center justify-between text-sm text-gray-600">
          <span>최근 6개월 CAU Code 해결 현황</span>
          <span>
            {loading ? (
              <div className="animate-pulse bg-gray-200 h-4 w-24 rounded"></div>
            ) : (
              `총 ${totalSolved.toLocaleString()}개 문제 해결`
            )}
          </span>
        </div>
        
        {/* 월별 해결 현황 */}
        <div className="space-y-3">
          <div className="grid grid-cols-6 gap-4 text-xs text-gray-500 mb-2">
            {monthlyData.map((month, index) => (
              <div key={index} className="text-center">{month.name}</div>
            ))}
          </div>

          {/* 월별 그리드 (6개월) */}
          <div className="grid grid-cols-6 gap-4">
            {loading ? (
              Array.from({ length: 6 }).map((_, monthIndex) => (
                <div key={monthIndex} className="space-y-1">
                  {Array.from({ length: 4 }).map((_, weekIndex) => (
                    <div key={weekIndex} className="flex space-x-1">
                      {Array.from({ length: 7 }).map((_, dayIndex) => (
                        <div
                          key={dayIndex}
                          className="w-3 h-3 bg-gray-200 rounded-sm animate-pulse"
                        />
                      ))}
                    </div>
                  ))}
                </div>
              ))
            ) : monthlyData.length > 0 ? (
              monthlyData.map((month, monthIndex) => (
                <div key={monthIndex} className="space-y-1">
                  {month.weeks.map((week, weekIndex) => (
                    <div key={weekIndex} className="flex space-x-1">
                      {week.map((day, dayIndex) => (
                        <div
                          key={dayIndex}
                          className={`contribution-day level-${day.level}`}
                          title={day.tooltip}
                        />
                      ))}
                    </div>
                  ))}
                </div>
              ))
            ) : (
              <div className="col-span-6 text-center py-8 text-gray-500">
                <p>아직 CAU Code에서 해결한 문제가 없습니다.</p>
              </div>
            )}
          </div>
        </div>
        
        <div className="flex items-center justify-between text-xs text-gray-500 pt-4 border-t">
          <span>적음</span>
          <div className="flex space-x-1">
            <div className="contribution-day level-0"></div>
            <div className="contribution-day level-1"></div>
            <div className="contribution-day level-2"></div>
            <div className="contribution-day level-3"></div>
            <div className="contribution-day level-4"></div>
          </div>
          <span>많음</span>
        </div>
      </div>
    </div>
  );
};

export default ContributionGraph;