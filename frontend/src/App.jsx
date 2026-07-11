import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import AppLayout from './layouts/AppLayout'

import LoginPage from './pages/LoginPage'
import RegisterCompanyPage from './pages/RegisterCompanyPage'
import DashboardPage from './pages/DashboardPage'
import CompanyProfilePage from './pages/CompanyProfilePage'
import CompanyProfileEditPage from './pages/CompanyProfileEditPage'
import BranchesPage from './pages/BranchesPage'
import UsersPage from './pages/UsersPage'
import RolesPage from './pages/RolesPage'
import RoleEditPage from './pages/RoleEditPage'
import AiAssistantPage from './pages/AiAssistantPage'

function ProtectedRoute({ children }) {
  const { user, loading } = useAuth()
  if (loading) {
    return (
      <div className="h-screen w-screen flex items-center justify-center bg-slate-50">
        <div className="h-8 w-8 rounded-full border-2 border-navy-600 border-t-transparent animate-spin" />
      </div>
    )
  }
  if (!user) return <Navigate to="/login" replace />
  return children
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterCompanyPage />} />

      <Route
        path="/"
        element={
          <ProtectedRoute>
            <AppLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="ai-assistant" element={<AiAssistantPage />} />
        <Route path="company-profile" element={<CompanyProfilePage />} />
        <Route path="company-profile/edit" element={<CompanyProfileEditPage />} />
        <Route path="branches" element={<BranchesPage />} />
        <Route path="users" element={<UsersPage />} />
        <Route path="roles" element={<RolesPage />} />
        <Route path="roles/:roleId" element={<RoleEditPage />} />
      </Route>

      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  )
}
