import React, { useState } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import Login from './pages/Login';
import Register from './pages/Register';
import MainLayout from './components/layout/MainLayout';

const AppContent = () => {
  const { user } = useAuth();
  const [authPage, setAuthPage] = useState('login');

  if (!user) {
    if (authPage === 'register') return <Register onLogin={() => setAuthPage('login')} />;
    return <Login onRegister={() => setAuthPage('register')} />;
  }

  return <MainLayout />;
};

export default function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}
