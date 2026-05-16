import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import SubmitBusiness from './pages/SubmitBusiness';
import Login from './pages/Login';
import Register from './pages/Register';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const token = localStorage.getItem('token');
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <SubmitBusinessWithLogout />
            </ProtectedRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}

function SubmitBusinessWithLogout() {
  return <SubmitBusiness />;
}

export default App;