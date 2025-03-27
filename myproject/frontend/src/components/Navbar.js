// components/Navbar.js
import React from 'react';
import { useNavigate } from 'react-router-dom';

const Navbar = () => {
  const navigate = useNavigate();
  const isLoggedIn = !!localStorage.getItem('access');  // JWT token presence

  const handleLogout = () => {
    localStorage.removeItem('access');
    localStorage.removeItem('refresh');
    navigate('/login');
  };

  return (
    <nav className="navbar">
      <div className="navbar-left">
        <h1>Your App</h1>
      </div>

      {isLoggedIn && (
        <div className="navbar-right">
          <div className="dropdown">
            <img
              src="/profile-icon.png"
              alt="Profile"
              className="profile-icon"
            />
            <div className="dropdown-content">
              <button onClick={handleLogout}>Sign Out</button>
            </div>
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
