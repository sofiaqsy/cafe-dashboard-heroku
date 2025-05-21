import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';
import { 
  HomeIcon, 
  CubeIcon, 
  BanknotesIcon, 
  ChartBarIcon, 
  Cog6ToothIcon,
  ArrowLeftOnRectangleIcon,
  XMarkIcon,
  Bars3Icon
} from '@heroicons/react/24/outline';

const Sidebar = () => {
  const [collapsed, setCollapsed] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // Navigation items
  const navItems = [
    { name: 'Dashboard', path: '/', icon: HomeIcon },
    { name: 'Inventario', path: '/inventory', icon: CubeIcon },
    { name: 'Finanzas', path: '/financial', icon: BanknotesIcon },
    { name: 'Reportes', path: '/reports', icon: ChartBarIcon },
    { name: 'Configuración', path: '/settings', icon: Cog6ToothIcon },
  ];

  const toggleSidebar = () => {
    setCollapsed(!collapsed);
  };

  const toggleMobileMenu = () => {
    setMobileMenuOpen(!mobileMenuOpen);
  };

  // Common styles for NavLink
  const getLinkClasses = ({ isActive }) => {
    return `flex items-center px-4 py-3 transition-colors rounded-lg ${
      isActive 
        ? 'bg-coffee-100 text-coffee-800' 
        : 'text-gray-700 hover:bg-coffee-50'
    }`;
  };

  return (
    <>
      {/* Mobile Menu Button */}
      <button 
        className="lg:hidden fixed top-4 left-4 z-50 p-2 rounded-md bg-coffee-50 text-coffee-700"
        onClick={toggleMobileMenu}
      >
        <Bars3Icon className="h-6 w-6" />
      </button>
      
      {/* Mobile Sidebar */}
      <div className={`fixed inset-0 z-40 lg:hidden ${mobileMenuOpen ? 'block' : 'hidden'}`}>
        {/* Backdrop */}
        <div 
          className="fixed inset-0 bg-black bg-opacity-50" 
          onClick={toggleMobileMenu}
        ></div>
        
        {/* Sidebar Content */}
        <div className="fixed inset-y-0 left-0 w-64 bg-white shadow-lg transform transition-transform">
          <div className="flex items-center justify-between h-16 px-4 border-b">
            <h1 className="text-xl font-bold text-coffee-800">Café Dashboard</h1>
            <button onClick={toggleMobileMenu}>
              <XMarkIcon className="h-6 w-6 text-gray-500" />
            </button>
          </div>
          <nav className="mt-4 px-2 space-y-1">
            {navItems.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                className={getLinkClasses}
                onClick={() => setMobileMenuOpen(false)}
              >
                <item.icon className="h-5 w-5 mr-3" />
                <span>{item.name}</span>
              </NavLink>
            ))}
          </nav>
        </div>
      </div>
      
      {/* Desktop Sidebar */}
      <aside className={`hidden lg:block bg-white shadow-lg transition-all ${collapsed ? 'w-20' : 'w-64'}`}>
        {/* Sidebar Header */}
        <div className="flex items-center justify-between h-16 px-4 border-b">
          {!collapsed && <h1 className="text-xl font-bold text-coffee-800">Café Dashboard</h1>}
          <button 
            onClick={toggleSidebar}
            className={`p-1 rounded-full text-gray-400 hover:bg-gray-100 ${collapsed ? 'mx-auto' : ''}`}
          >
            <ArrowLeftOnRectangleIcon 
              className={`h-5 w-5 transform transition-transform ${collapsed ? 'rotate-180' : ''}`}
            />
          </button>
        </div>
        
        {/* Sidebar Navigation */}
        <nav className="mt-4 px-2 space-y-1">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={getLinkClasses}
              title={collapsed ? item.name : ''}
            >
              <item.icon className={`h-5 w-5 ${collapsed ? 'mx-auto' : 'mr-3'}`} />
              {!collapsed && <span>{item.name}</span>}
            </NavLink>
          ))}
        </nav>
      </aside>
    </>
  );
};

export default Sidebar;
