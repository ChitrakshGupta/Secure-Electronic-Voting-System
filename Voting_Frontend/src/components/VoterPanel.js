import React, { useState, useEffect,useCallback } from "react";
import axios from "axios";
import "../styles/VoterPanel.css";

function VoterPanel({ token, userId, onLogout }) {
  const [candidates, setCandidates] = useState([]);
  const [selectedCandidate, setSelectedCandidate] = useState(null);
  const [message, setMessage] = useState("");
  const [eligibilityMessage, setEligibilityMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [isEligible, setIsEligible] = useState(null); // Track eligibility
  const [timer, setTimer] = useState(30); // Timer for ineligible voters
  const [confirmingVote, setConfirmingVote] = useState(false); // Track confirmation state
  const [voteComplete, setVoteComplete] = useState(false); // Track vote completion
  const [voteTimer, setVoteTimer] = useState(120); // Timer for casting vote

  useEffect(() => {
    if (isEligible && !voteComplete) {
      const countdown = setInterval(() => {
        setVoteTimer((prevTimer) => {
          if (prevTimer <= 1) {
            clearInterval(countdown);
            onLogout(); // Auto logout after timeout
          }
          return prevTimer - 1;
        });
      }, 1000);

      return () => clearInterval(countdown); // Cleanup on unmount or state change
    }
  }, [isEligible, voteComplete, onLogout]);

  useEffect(() => {
    if (isEligible === false) {
      const countdown = setInterval(() => {
        setTimer((prevTimer) => {
          if (prevTimer <= 1) {
            clearInterval(countdown);
            onLogout(); // Auto logout after countdown ends
          }
          return prevTimer - 1;
        });
      }, 1000);
  
      return () => clearInterval(countdown); // Cleanup the interval on component unmount or state change
    }
  }, [isEligible, onLogout]);
  

  const fetchCandidates = useCallback(async () => {
    try {
      setLoading(true);
      const response = await axios.get("http://localhost:5000/candidates", {
        headers: { Authorization: `Bearer ${token}` },
      });
      setCandidates(response.data.candidates);
    } catch (error) {
      setMessage("Failed to load candidates.");
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    // Automatically check eligibility on component mount
    const checkEligibility = async () => {
      try {
        setLoading(true);
        const response = await axios.post(
          "http://localhost:5000/check-eligibility",
          { voter_id: userId },
          { headers: { Authorization: `Bearer ${token}` } }
        );

        const { voter_id, message } = response.data;
        setEligibilityMessage(message);

        if (voter_id === null) {
          setIsEligible(false); // User is not eligible
        } else {
          setIsEligible(true); // User is eligible
        }
      } catch (error) {
        setEligibilityMessage(
          error.response?.data?.error || "Failed to check eligibility."
        );
        setIsEligible(false);
      } finally {
        setLoading(false);
      }
    };

    checkEligibility();
  }, [token, userId]);

  // Fetch candidates if eligible
  useEffect(() => {
    if (isEligible) {
      fetchCandidates();
    }
  }, [isEligible,fetchCandidates]); // Trigger fetch only when eligibility is determined

  const handleVote = () => {
    if (!selectedCandidate) {
      setMessage("Please select a candidate.");
      return;
    }
    setConfirmingVote(true); // Show confirmation dialog
  };

  const confirmVote = async () => {
    try {
      setLoading(true);
      const response = await axios.post(
        "http://localhost:5000/cast-vote",
        {
          voter_id: userId,
          selected_candidate_index: candidates.findIndex(
            (c) => c.id === selectedCandidate
          ),
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setMessage(response.data.message);
      setVoteComplete(true); // Mark vote as completed
      setVoteTimer(0); // Stop the timer
      setTimeout(() => {
        onLogout();
      }, 3000); // Auto logout after 3 seconds
    } catch (error) {
      setMessage(error.response?.data?.message || "Failed to cast vote.");
    } finally {
      setLoading(false);
      setConfirmingVote(false); // Close confirmation dialog
    }
  };


  const cancelVote = () => {
    setConfirmingVote(false); // Cancel the confirmation dialog
    setMessage("Vote canceled. You can select another candidate.");
  };

  const handleCardClick = (candidateId) => {
    setSelectedCandidate(candidateId);
  };
  
  return (
    <div className="voter-panel">
      <h2 className="voter-panel-header">Voter Panel</h2>
      {loading ? (
        <p className="eligibility-message">Loading...</p>
      ) : isEligible === null ? (
        <p className="eligibility-message" >Checking eligibility...</p>
      ) : isEligible ? (
        <>
          {voteComplete ? (
            <p className="eligibility-message">{message}</p> // Show success message after vote completion
          ) : confirmingVote ? (
            <div className="vote-confirmation">
              <p>
                You are about to vote for{" "}
                <strong>
                  {
                    candidates.find((candidate) => candidate.id === selectedCandidate)
                      ?.name
                  }
                </strong>
                . Are you sure?
              </p>
              <button onClick={confirmVote} disabled={loading} className="vote-confirmation-button voter-panel-button">
                {loading ? "Confirming..." : "Confirm"}
              </button>
              <button onClick={cancelVote}className="vote-confirmation-button">Cancel</button>
            </div>
          ) : (
            <>
              <h3  className="voter-panel-header">Select a Candidate</h3>
              <p className="vote-timer">Time remaining to cast your vote: {voteTimer} seconds</p>
              {candidates.length > 0 ? (
                <ul className="candidate-list">
                  {candidates.map((candidate) => (
                    <li
                    key={candidate.id}
                    className={`candidate-item ${
                      selectedCandidate === candidate.id ? "selected" : ""
                    }`}
                    onClick={() => handleCardClick(candidate.id)}
                  >
                    <img
                      src={`http://localhost:5000/photos_symbol/${candidate.id}.jpg`}
                      alt={`${candidate.name} Symbol`}
                      className="candidate-image"
                  />
                    <span className="candidate-name">{candidate.name}</span>
                  </li>
                  
                  ))}
                </ul>
              ) : (
                <p className="eligibility-message">No candidates available.</p>
              )}

              <button onClick={handleVote} disabled={loading} className="voter-panel-button">
                {loading ? "Casting Vote..." : "Cast Vote"}
              </button>
            </>
          )}
        </>
      ) : (
        <>
          <p className="eligibility-message">{eligibilityMessage || "You are not eligible to vote."}</p>
          <p className="vote-timer">Logging out in {timer} seconds...</p>
          <button onClick={onLogout} className="voter-panel-button">Exit</button>
        </>
      )}
    </div>
  );
}

export default VoterPanel;
