import { BrowserRouter, Routes, Route, NavLink, useLocation } from 'react-router-dom';
import UploadPage from './pages/UploadPage';
import ResultsPage from './pages/ResultsPage';
import HistoryPage from './pages/HistoryPage';
import ModelInfoPage from './pages/ModelInfoPage';
import './index.css';

function Navbar() {
  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <div className="brand-icon">⚗</div>
        <span>Pharma<b>QC</b></span>
        <span className="navbar-badge">AI</span>
      </div>
      <div className="navbar-links">
        {[
          { to: '/',        label: 'Upload',  icon: '↑' },
          { to: '/history', label: 'History', icon: '⏱' },
          { to: '/model',   label: 'Model',   icon: '⊞' },
        ].map(({ to, label, icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}
          >
            {icon} {label}
          </NavLink>
        ))}
      </div>
    </nav>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <div className="page-shell">
        <Navbar />
        <Routes>
          <Route path="/"             element={<UploadPage />} />
          <Route path="/results/:id"  element={<ResultsPage />} />
          <Route path="/history"      element={<HistoryPage />} />
          <Route path="/model"        element={<ModelInfoPage />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}
