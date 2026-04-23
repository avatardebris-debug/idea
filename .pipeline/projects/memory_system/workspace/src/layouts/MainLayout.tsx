import { Outlet, Link, useLocation } from 'react-router-dom';
import './MainLayout.css';

const MainLayout = () => {
  const location = useLocation();

  const navItems = [
    { path: '/', label: 'Home' },
    { path: '/card-exercise', label: 'Card Exercise' },
    { path: '/number-exercise', label: 'Number Exercise' },
    { path: '/memory-palace', label: 'Memory Palace' },
  ];

  return (
    <div className="main-layout">
      <nav className="navigation-bar">
        <div className="nav-brand">
          <Link to="/">Memory System</Link>
        </div>
        <ul className="nav-menu">
          {navItems.map((item) => (
            <li key={item.path} className={`nav-item ${location.pathname === item.path ? 'active' : ''}`}>
              <Link to={item.path}>{item.label}</Link>
            </li>
          ))}
        </ul>
      </nav>
      <main className="main-content">
        <Outlet />
      </main>
      <footer className="main-footer">
        <p>Memory System v1.0.0 - Train your memory with proven techniques</p>
      </footer>
    </div>
  );
};

export default MainLayout;
