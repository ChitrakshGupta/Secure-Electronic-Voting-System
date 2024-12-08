import React, { useState, useEffect,useCallback } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import "../styles/AdminPanel.css";

function AdminPanel({ token, onLogout }) {
  const [activeSection, setActiveSection] = useState("voting");
  const [voterData, setVoterData] = useState({ username: "", email: "" });
  const [candidateName, setCandidateName] = useState("");
  const [voters, setVoters] = useState([]);
  const [candidates, setCandidates] = useState([]); // Candidate list
  const [editVoter, setEditVoter] = useState(null);
  const [editCandidate, setEditCandidate] = useState(null); // Candidate being edited
  const [editData, setEditData] = useState({ username: "", email: "", photo: null });
  const [editCandidateData, setEditCandidateData] = useState({ name: "", symbol: null }); // Candidate edit data
  const [results, setResults] = useState(null);
  const [message, setMessage] = useState("");
  const [photo, setPhoto] = useState(null);
  const [isVotingActive, setIsVotingActive] = useState(false);
  const [loading, setLoading] = useState(false); // To show loading indicator
  const navigate = useNavigate();

  const handlePhotoChange = (e) => {
    setPhoto(e.target.files[0]);
  };

  const fetchVoters = useCallback(async () => {
    try {
      const response = await axios.get("http://localhost:5000/voters", {
        headers: { Authorization: `Bearer ${token}` },
      });
      setVoters(response.data.voters);
    } catch (error) {
      setMessage("Failed to fetch voters.");
    }
  }, [token]);
  
  const fetchCandidates = useCallback(async () => {
    try {
      const response = await axios.get("http://localhost:5000/candidates", {
        headers: { Authorization: `Bearer ${token}` },
      });
      setCandidates(response.data.candidates);
    } catch (error) {
      setMessage("Failed to fetch candidates.");
    }
  }, [token]);
  

  const handleAddVoter = async () => {
    const formData = new FormData();
    formData.append("username", voterData.username);
    formData.append("email", voterData.email);
    if (photo) formData.append("photo", photo);
  
    try {
      const response = await axios.post("http://localhost:5000/add-voter", formData, {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "multipart/form-data",
        },
      });
      setMessage(response.data.message || "Voter added successfully!");
      setVoterData({ username: "", email: "" });
      setPhoto(null);
      fetchVoters();
    } catch (error) {
      setMessage("Failed to add voter.");
    }
  };

  const handleUpdateVoter = async (voterId) => {
    const formData = new FormData();
    formData.append("username", editData.username);
    formData.append("email", editData.email);
    if (editData.photo) formData.append("photo", editData.photo);

    try {
      const response = await axios.put(
        `http://localhost:5000/update-voter/${voterId}`,
        formData,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setMessage(response.data.message || "Voter updated successfully!");
      setEditVoter(null);
      fetchVoters();
    } catch (error) {
      setMessage("Failed to update voter.");
    }
  };

  const handleDeleteVoter = async (voterId) => {
    try {
      const response = await axios.delete(`http://localhost:5000/delete-voter/${voterId}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setMessage(response.data.message || "Voter deleted successfully!");
      fetchVoters();
    } catch (error) {
      setMessage("Failed to delete voter.");
    }
  };

  const handleAddCandidate = async () => {
    if (!candidateName.trim() || !photo) {
      setMessage("Candidate name and symbol are required.");
      return;
    }

    const formData = new FormData();
    formData.append("name", candidateName);
    formData.append("symbol", photo);

    try {
      const response = await axios.post(
        "http://localhost:5000/add-candidate",
        formData,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setMessage(response.data.message || "Candidate added successfully!");
      setCandidateName("");
      setPhoto(null);
      fetchCandidates();
    } catch (error) {
      setMessage("Failed to add candidate.");
    }
  };

  const handleUpdateCandidate = async (candidateId) => {
    const formData = new FormData();
    formData.append("name", editCandidateData.name);
    if (editCandidateData.symbol) formData.append("symbol", editCandidateData.symbol);

    try {
      const response = await axios.put(
        `http://localhost:5000/update-candidate/${candidateId}`,
        formData,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setMessage(response.data.message || "Candidate updated successfully!");
      setEditCandidate(null);
      fetchCandidates();
    } catch (error) {
      setMessage("Failed to update candidate.");
    }
  };

  const handleDeleteCandidate = async (candidateId) => {
    try {
      const response = await axios.delete(`http://localhost:5000/delete-candidate/${candidateId}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setMessage(response.data.message || "Candidate deleted successfully!");
      fetchCandidates();
    } catch (error) {
      setMessage("Failed to delete candidate.");
    }
  };

  const handleStartVoting = async () => {
    setLoading(true);
    try {
      const response = await axios.post("http://localhost:5000/start-voting", {}, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setMessage(response.data.message || "Voting session started!");
      setIsVotingActive(true);
    } catch (error) {
      setMessage("Failed to start voting session.");
    }
    finally {
      setLoading (false);
    }
  };

  const handleStopVoting = async () => {
    setLoading(true);
    try {
      await axios.post("http://localhost:5000/stop-voting", {}, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setMessage("Voting session stopped!");
      setIsVotingActive(false);
    } catch (error) {
      setMessage("Failed to stop voting session.");
    }finally {
      setLoading (false); 
    }
  };

  const handleViewResults = async () => {
    try {
      const response = await axios.get("http://localhost:5000/view-results", {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (response.data.success) {
        setResults(response.data.results);
      } else {
        setMessage("Failed to fetch results.");
      }
    } catch (error) {
      setMessage("Failed to fetch results.");
    }
  };

  const handleExit = async () => {
    await onLogout();
    navigate("/");
  };

  const handleSectionChange = (section) => {
    if (isVotingActive && section !== "voting") return;
    setActiveSection(section);
    setMessage("");
    if (section === "exit") handleExit();
  };

  const handleEditVoterChange = (field, value) => {
    setEditData((prevData) => ({
      ...prevData,
      [field]: value,
    }));
  };
  
  useEffect(() => {
    if (activeSection === "voter") fetchVoters();
    if (activeSection === "candidate") fetchCandidates();
  }, [activeSection, fetchVoters, fetchCandidates]);
  

  const renderSection = () => {
    switch (activeSection) {
      case "voting":
        return (
          <div className="admin-section">
            <h3 className="admin-section-title">Voting Session</h3>
            <button
              className={`admin-button start ${loading ? "loading" : ""}`}
              onClick={handleStartVoting}
              disabled={isVotingActive || loading}
            >
              {loading ? "Starting..." : "Start Voting"}
            </button>
            <button
              className={`admin-button stop ${loading ? "loading" : ""}`}
              onClick={handleStopVoting}
              disabled={!isVotingActive || loading}
            >
              {loading ? "Stopping..." : "Stop Voting"}
            </button>
          </div>
        );
  
      case "voter":
        return (
          <div className="admin-section">
            <h3 className="admin-section-title">Add Voter</h3>
            <div className="admin-voter-form">
              <input
                type="text"
                className="admin-voter-input"
                placeholder="Username"
                value={voterData.username}
                onChange={(e) => setVoterData({ ...voterData, username: e.target.value })}
              />
              <input
                type="email"
                className="admin-voter-input"
                placeholder="Email"
                value={voterData.email}
                onChange={(e) => setVoterData({ ...voterData, email: e.target.value })}
              />
              <input
                type="file"
                className="admin-voter-input"
                accept="image/*"
                onChange={handlePhotoChange}
              />
              <div className="admin-button-container">
                <button className="admin-button add" onClick={handleAddVoter}>
                  Add Voter
                </button>
              </div>
            </div>
            <h3 className="admin-section-title">List of Voters</h3>
            <ul className="admin-list">
              {voters.map((voter) => (
                <li key={voter.id} className="admin-list-item">
                  <div className="voter-details">
                    <img
                      src={`http://localhost:5000/photos/${voter.id}.jpg`}
                      alt="Voter"
                      className="admin-list-image"
                    />
                    <div className="voter-info">
                      <span className="admin-list-name">
                        {voter.username}
                      </span>
                      <span className="admin-list-email">
                         {voter.email}
                      </span>
                    </div>
                  </div>
                  {editVoter === voter.id ? (
                    <div className="admin-edit-controls">
                      <div className="admin-edit-form">
                        <input
                          type="text"
                          placeholder="Username"
                          className="admin-input edit"
                          value={editData.username}
                          onChange={(e) => handleEditVoterChange("username", e.target.value)}
                        />
                        <input
                          type="email"
                          placeholder="Email"
                          className="admin-input edit"
                          value={editData.email}
                          onChange={(e) => handleEditVoterChange("email", e.target.value)}
                        />
                        <input
                          type="file"
                          className="admin-input edit"
                          accept="image/*"
                          onChange={(e) => handleEditVoterChange("photo", e.target.files[0])}
                        />
                      </div>
                      <div className="admin-edit-buttons">
                        <button
                          className="admin-button save"
                          onClick={() => handleUpdateVoter(voter.id)}
                        >
                          Save
                        </button>
                        <button
                          className="admin-button cancel"
                          onClick={() => setEditVoter(null)}
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div className="admin-actions">
                      <button
                        className="admin-button edit"
                        onClick={() => {
                          setEditVoter(voter.id);
                          setEditData({ username: voter.username, email: voter.email, photo: null });
                        }}
                      >
                        Edit
                      </button>
                      <button
                        className="admin-button delete"
                        onClick={() => handleDeleteVoter(voter.id)}
                      >
                        Delete
                      </button>
                    </div>
                  )}
                </li>
              ))}
            </ul>
          </div>
        );
  
      case "candidate":
        return (
          <div className="admin-section">
            <h3 className="admin-section-title">Add Candidate</h3>
            <div className="admin-candidate-form">
              <input
                type="text"
                className="admin-input"
                placeholder="Candidate Name"
                value={candidateName}
                onChange={(e) => setCandidateName(e.target.value)}
              />
              <input
                type="file"
                className="admin-input"
                accept="image/*"
                onChange={handlePhotoChange}
              />
              <div className="admin-button-container">
                <button className="admin-button add" onClick={handleAddCandidate}>
                  Add Candidate
                </button>
              </div>
            </div>
            <h3 className="admin-section-title">List of Candidates</h3>
            <ul className="admin-list">
              {candidates.map((candidate) => (
                <li key={candidate.id} className="admin-list-item">
                  <img
                    src={`http://localhost:5000/photos_symbol/${candidate.id}.jpg`}
                    alt="Symbol"
                    className="admin-list-image"
                  />
                  <span className="admin-list-name">{candidate.name}</span>
                  {editCandidate === candidate.id ? (
                    <div className="admin-edit-controls">
                      <div className="admin-edit-form">
                        <input
                          type="text"
                          className="admin-input edit"
                          value={editCandidateData.name}
                          onChange={(e) =>
                            setEditCandidateData({ ...editCandidateData, name: e.target.value })
                          }
                        />
                        <input
                          type="file"
                          className="admin-input edit"
                          accept="image/*"
                          onChange={(e) =>
                            setEditCandidateData({
                              ...editCandidateData,
                              symbol: e.target.files[0],
                            })
                          }
                        />
                      </div>
                      <div className="admin-edit-buttons">
                        <button
                          className="admin-button save"
                          onClick={() => handleUpdateCandidate(candidate.id)}
                        >
                          Save
                        </button>
                        <button
                          className="admin-button cancel"
                          onClick={() => setEditCandidate(null)}
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div className="admin-actions">
                      <button
                        className="admin-button edit"
                        onClick={() => {
                          setEditCandidate(candidate.id);
                          setEditCandidateData({ name: candidate.name, symbol: null });
                        }}
                      >
                        Edit
                      </button>
                      <button
                        className="admin-button delete"
                        onClick={() => handleDeleteCandidate(candidate.id)}
                      >
                        Delete
                      </button>
                    </div>
                  )}
                </li>
              ))}
            </ul>
          </div>
        );
  
      case "result":
        return (
          <div className="admin-section">
            <h3 className="admin-section-title">Results</h3>
            <button className="admin-button fetch" onClick={handleViewResults}>
              Fetch Results
            </button>
            {results && (
              <table className="admin-result-table">
                <thead>
                  <tr>
                    <th>Candidate</th>
                    <th>Votes</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(results)
                    .sort((a, b) => b[1] - a[1])
                    .map(([candidate, votes]) => (
                      <tr key={candidate}>
                        <td>{candidate}</td>
                        <td>{votes}</td>
                      </tr>
                    ))}
                </tbody>
              </table>
            )}
          </div>
        );
  
      default:
        return <h3 className="admin-section-title">Welcome to the Admin Panel</h3>;
    }
  };
  
  

  return (
    <div className="admin-container">
      <aside className="admin-sidebar">
        <h2 className="admin-sidebar-title">Admin Panel</h2>
        <ul className="admin-sidebar-menu">
          <li className="admin-sidebar-item" onClick={() => handleSectionChange("voting")}>Voting Session</li>
          <li className="admin-sidebar-item" onClick={() => handleSectionChange("voter")}>Voter Management</li>
          <li className="admin-sidebar-item" onClick={() => handleSectionChange("candidate")}>Candidate Management</li>
          <li className="admin-sidebar-item" onClick={() => handleSectionChange("result")}>Result</li>
          <li className="admin-sidebar-item" onClick={() => handleSectionChange("exit")}>Exit</li>
        </ul>
      </aside>
      <main className="admin-content">
        {renderSection()}
        {message && <p style={{ color: "green" }}>{message}</p>}
      </main>
    </div>
  );
}

export default AdminPanel;
