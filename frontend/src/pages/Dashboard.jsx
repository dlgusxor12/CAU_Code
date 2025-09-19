import React from 'react';
import UserStats from '../components/dashboard/UserStats';
import TodayProblems from '../components/dashboard/TodayProblems';
import ReviewProblems from '../components/dashboard/ReviewProblems';
import ContributionGraph from '../components/dashboard/ContributionGraph';
import QuickActions from '../components/dashboard/QuickActions';
import WeeklyStats from '../components/dashboard/WeeklyStats';
import RecentActivity from '../components/dashboard/RecentActivity';

const Dashboard = () => {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* User Stats Section */}
      <UserStats />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column */}
        <div className="lg:col-span-2 space-y-6">
          {/* Today's Problems */}
          <TodayProblems />

          {/* Review Problems */}
          <ReviewProblems />

          {/* Contribution Graph */}
          <ContributionGraph />
        </div>

        {/* Right Column */}
        <div className="space-y-6">
          {/* Quick Actions */}
          <QuickActions />

          {/* Weekly Statistics */}
          <WeeklyStats />

          {/* Recent Activity */}
          <RecentActivity />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;