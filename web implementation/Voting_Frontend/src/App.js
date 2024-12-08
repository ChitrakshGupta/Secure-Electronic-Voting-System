import React, { useState } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import AdminPanel from "./components/AdminPanel";
import VoterPanel from "./components/VoterPanel";
import Login from "./components/Login";
import "./styles/Spinner.css"; // Import spinner styles

function App() {
  const [userRole, setUserRole] = useState(null); // Stores the role ('admin' or 'voter')
  const [token, setToken] = useState(null); // Stores the authentication token
  const [userId, setUserId] = useState(null); // Stores the logged-in user's ID (for voters)
  const [loading, setLoading] = useState(false); // Tracks logout loading state

  const handleLogin = (role, authToken, id = null) => {
    setUserRole(role);
    setToken(authToken);
    if (id) setUserId(id); // Only set userId for voters
  };

  const handleLogout = async () => {
    setLoading(true); // Show loading spinner
    try {
      // Simulate an API call or logout delay
      await new Promise((resolve) => setTimeout(resolve, 1500));
      setUserRole(null);
      setToken(null);
      setUserId(null);
    } catch (error) {
      console.error("Logout failed:", error);
    } finally {
      setLoading(false); // Hide loading spinner
    }
  };

  return (
    <Router>
      {loading ? (
        <div className="spinner-container">
          <div className="spinner"></div>
          <p>Logging out...</p>
        </div>
      ) : (
        <Routes>
          {/* Login Route */}
          <Route
            path="/"
            element={
              !userRole ? (
                <Login onLogin={handleLogin} />
              ) : userRole === "admin" ? (
                <Navigate to="/admin" />
              ) : (
                <Navigate to="/voter" />
              )
            }
          />

          {/* Admin Panel Route */}
          <Route
            path="/admin"
            element={
              userRole === "admin" ? (
                <AdminPanel token={token} onLogout={handleLogout} />
              ) : (
                <Navigate to="/" />
              )
            }
          />

          {/* Voter Panel Route */}
          <Route
            path="/voter"
            element={
              userRole === "voter" ? (
                <VoterPanel token={token} userId={userId} onLogout={handleLogout} />
              ) : (
                <Navigate to="/" />
              )
            }
          />

          {/* Catch-all Route */}
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      )}
    </Router>
  );
}

export default App;
