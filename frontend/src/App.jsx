import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navigation from './components/Navigation';
import Footer from './components/Footer';
import Dashboard from './pages/Dashboard';
import Problems from './pages/Problems';
import Guide from './pages/Guide';
import Feedback from './pages/Feedback';
import Ranking from './pages/Ranking';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-[#F2F8FA] flex flex-col">
        <Navigation />
        <main className="flex-grow">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/problems" element={<Problems />} />
            <Route path="/guide" element={<Guide />} />
            <Route path="/feedback" element={<Feedback />} />
            <Route path="/ranking" element={<Ranking />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </Router>
  );
}

export default App;