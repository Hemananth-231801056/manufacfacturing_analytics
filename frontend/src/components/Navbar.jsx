import { useState } from 'react';
import { NavLink } from 'react-router-dom';
import { Beaker, Menu, X } from 'lucide-react';
import './Navbar.css';

function Navbar() {
  const [isOpen, setIsOpen] = useState(false);

  const toggleMenu = () => setIsOpen(!isOpen);

  return (
    <nav className="navbar glass-card">
      <div className="navbar-container">
        <NavLink to="/" className="navbar-brand">
          <Beaker className="brand-icon" size={24} />
          <span>PharmaBatch AI</span>
        </NavLink>

        <div className="mobile-menu-btn" onClick={toggleMenu}>
          {isOpen ? <X size={24} /> : <Menu size={24} />}
        </div>

        <div className={`nav-links ${isOpen ? 'active' : ''}`}>
          <NavLink to="/" className="nav-link" onClick={() => setIsOpen(false)}>Home</NavLink>
          <NavLink to="/about" className="nav-link" onClick={() => setIsOpen(false)}>About</NavLink>
          <NavLink to="/predict" className="nav-link" onClick={() => setIsOpen(false)}>Evaluate Batch</NavLink>
          <NavLink to="/history" className="nav-link" onClick={() => setIsOpen(false)}>History</NavLink>
          <NavLink to="/reports" className="nav-link" onClick={() => setIsOpen(false)}>Reports</NavLink>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
