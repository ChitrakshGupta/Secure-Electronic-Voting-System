from flask import Flask, jsonify
from flask_cors import CORS
from components.login import login_bp
from components.user_management import user_mgmt_bp
from components.candidate_management import candidate_mgmt_bp
from components.admin import start_voting
from components.voter_keys import generate_voter_keys
from components.tally_server import reset_votes, tally_votes, reset_voter_status
from components.eligibility import eligibility_bp
from components.voter import cast_vote_endpoint

app = Flask(__name__)
CORS(app)

# Register blueprints
app.register_blueprint(login_bp)
app.register_blueprint(user_mgmt_bp)
app.register_blueprint(candidate_mgmt_bp)
app.register_blueprint(eligibility_bp)
app.register_blueprint(cast_vote_endpoint)


@app.route('/start-voting', methods=['POST'])
def start_voting_endpoint():
    try:
        admin_result = start_voting()
        voter_keys_result = generate_voter_keys()
        reset_votes()
        reset_voter_status()
        combined_message = (
            "Voting session started successfully!\n"
            f"Admin Result: {admin_result['message']}\n"
            f"Voter Result: {voter_keys_result['message']}\n"
            "Votes reset and tally server ready."
        )
        return jsonify({"message": combined_message}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/stop-voting', methods=['POST'])
def stop_voting_endpoint():
    try:
        # Tally the votes
        tally_results = tally_votes()

        # Reset the has_voted column in the database
        reset_voter_status()

        # Format the results for display
        formatted_results = "\n".join(
            [f"Candidate {candidate_id}: {votes} votes" for candidate_id, votes in tally_results.items()]
        )
        combined_message = (
            "Voting session stopped successfully!\n"
            f"Tally Results:\n{formatted_results}"
        )
        return jsonify({"message": combined_message}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/view-results', methods=['GET'])
def view_results_endpoint():
    """
    Endpoint to view the results of the voting session.
    """
    try:
        results = tally_votes()
        return jsonify({"success": True, "results": results}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
