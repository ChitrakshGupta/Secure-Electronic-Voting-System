import React, { useState, useEffect } from 'react';
import axios from 'axios';
import "../styles/Login.css";

function Login({ onLogin }) {
  const [role, setRole] = useState(null);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [fileVerified, setFileVerified] = useState(false);
  const [adminDeviceId, setAdminDeviceId] = useState(null);

  // Check for the device ID file on the user's desktop
  useEffect(() => {
    const checkDeviceFile = async () => {
      try {
        console.log('Checking device file...');
        const response = await axios.get('http://localhost:4000/check-device');
        console.log('Response from backend:', response.data);
        if (response.data.success) {
          console.log('Device ID detected:', response.data.deviceId);
          setFileVerified(true);
          setAdminDeviceId(response.data.deviceId);
        } else {
          console.log('Device ID not detected');
          setFileVerified(false);
        }
      } catch (err) {
        console.error('Error checking device file:', err);
        setFileVerified(false);
      }
    };

    checkDeviceFile();
  }, []); // Empty dependency array to run this effect only once on component mount

  const handleRoleSelect = (selectedRole) => {
    setRole(selectedRole);
    setError(null); // Clear any previous errors
  };

  const handleLogin = async () => {
    if (!username || !password) {
      setError('Please fill in all fields.'); // Validate fields
      return;
    }

    setLoading(true);
    setError(null); // Clear previous errors

    try {
      const deviceId = role === 'admin' ? adminDeviceId : null; // Include device ID for admin
      const response = await axios.post(`http://localhost:5000/auth/login/${role}`, {
        username,
        password,
        deviceId,
      });

      if (response.data.token) {
        const userId = response.data.user_id || null; // Extract user ID if available
        console.log('userId:', userId);
        onLogin(role, response.data.token, userId); // Trigger the parent callback
      } else {
        setError('Invalid response from server.');
      }
    } catch (error) {
      console.error('Login failed:', error);
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
          {fileVerified && <button  className="role-button" onClick={() => handleRoleSelect('admin')}>Join as Admin</button>}
          <button  className="role-button" onClick={() => handleRoleSelect('voter')}>Join as Voter</button>
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
          <input
            type="password"
            placeholder="Password"
            value={password}
            className="input-field"
            onChange={(e) => setPassword(e.target.value)}
          />
          {error && <p style={{ color: 'red' }}>{error}</p>}
          <div  className="button-group">
          <button className="login-button" onClick={handleLogin} disabled={loading}>
            {loading ? 'Logging in...' : 'Login'}
          </button>
          <button className="back-button" onClick={() => setRole(null)}>Back</button>
        </div>
        </div>
      )}
    </div>
  );
}

export default Login;
