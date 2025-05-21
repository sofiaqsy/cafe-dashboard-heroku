import React from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import Header from './Header';

const Layout = () => {
  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <Sidebar />
      
      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <Header />
        
        {/* Main Content Area */}
        <main className="flex-1 overflow-y-auto p-4">
          <div className="container mx-auto">
            <Outlet />
          </div>
        </main>
        
        {/* Footer */}
        <footer className="bg-white p-4 shadow-inner">
          <div className="container mx-auto">
            <p className="text-center text-sm text-gray-500">
              © {new Date().getFullYear()} Café Dashboard - Todos los derechos reservados
            </p>
          </div>
        </footer>
      </div>
    </div>
  );
};

export default Layout;
