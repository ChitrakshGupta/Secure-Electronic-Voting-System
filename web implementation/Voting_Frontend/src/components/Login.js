import React, { useState, useEffect } from 'react';
import axios from 'axios';
import "../styles/Login.css";

function Login({ onLogin }) {
  const [role, setRole] = useState(null);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false); // State for password visibility
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [fileVerified, setFileVerified] = useState(false);
  const [adminDeviceId, setAdminDeviceId] = useState(null);

  useEffect(() => {
    const checkDeviceFile = async () => {
      try {
        const response = await axios.get('http://localhost:4000/check-device');
        if (response.data.success) {
          setFileVerified(true);
          setAdminDeviceId(response.data.deviceId);
        } else {
          setFileVerified(false);
        }
      } catch (err) {
        setFileVerified(false);
      }
    };

    checkDeviceFile();
  }, []);

  const handleRoleSelect = (selectedRole) => {
    setRole(selectedRole);
    setError(null);
  };

  const handleLogin = async () => {
    if (!username || !password) {
      setError('Please fill in all fields.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const deviceId = role === 'admin' ? adminDeviceId : null;
      const response = await axios.post(`http://localhost:5000/auth/login/${role}`, {
        username,
        password,
        deviceId,
      });

      if (response.data.token) {
        const userId = response.data.user_id || null;
        onLogin(role, response.data.token, userId);
      } else {
        setError('Invalid response from server.');
      }
    } catch (error) {
      setError(
        error.response?.data?.error || 'Login failed: Invalid credentials or unauthorized device.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      {!role ? (
        <div className="role-selection">
          <h2>Select Role</h2>
          {fileVerified && (
            <button className="role-button" onClick={() => handleRoleSelect('admin')}>
              Join as Admin
            </button>
          )}
          <button className="role-button" onClick={() => handleRoleSelect('voter')}>
            Join as Voter
          </button>
        </div>
      ) : (
        <div className="login-form">
  <h2>{role === 'admin' ? 'Admin' : 'Voter'} Login</h2>
  <input
    type="text"
    placeholder="Username"
    value={username}
    className="input-field"
    onChange={(e) => setUsername(e.target.value)}
  />
  <div className="password-container">
    <input
      type={showPassword ? 'text' : 'password'}
      placeholder="Password"
      value={password}
      className="input-password"
      onChange={(e) => setPassword(e.target.value)}
    />
    <button
      type="button"
      className="toggle-password"
      onClick={() => setShowPassword((prev) => !prev)}
    >
      {showPassword ? 'Hide' : 'Show'}
    </button>
  </div>
  {error && <p className="error-text">{error}</p>}
  <div className="button-group">
    <button className="login-button" onClick={handleLogin} disabled={loading}>
      {loading ? 'Logging in...' : 'Login'}
    </button>
    <button className="back-button" onClick={() => setRole(null)}>
      Back
    </button>
  </div>
</div>

      )}
    </div>
  );
}

export default Login;
