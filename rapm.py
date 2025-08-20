import numpy as np
from sklearn.linear_model import Ridge
from utils import read_video
from trackers import PlayerTracker, BallTracker
from team_assigner import TeamAssigner
from ball_aquisition import BallAquisitionDetector
from pass_interception_rebound_shot_attempt_detector import PassInterceptionReboundShotAttemptDetector

def calculate_rapm(video_path, player_tracker_path, ball_tracker_path, stub_path):
    # Read video frames
    video_frames = read_video(video_path)

    # Initialize trackers and detectors
    player_tracker = PlayerTracker(player_tracker_path)
    ball_tracker = BallTracker(ball_tracker_path)
    team_assigner = TeamAssigner()
    ball_aquisition_detector = BallAquisitionDetector()
    event_detector = PassInterceptionReboundShotAttemptDetector()

    # Get player and ball tracks
    player_tracks = player_tracker.get_object_tracks(video_frames, read_from_stub=True, stub_path=f"{stub_path}/player_track_stubs.pkl")
    ball_tracks = ball_tracker.get_object_tracks(video_frames, read_from_stub=True, stub_path=f"{stub_path}/ball_track_stubs.pkl")

    # Assign teams
    player_assignment = team_assigner.get_player_teams_across_frames(video_frames, player_tracks, read_from_stub=True, stub_path=f"{stub_path}/player_assignment_stub.pkl")

    # Detect ball possession
    ball_aquisition = ball_aquisition_detector.detect_ball_possession(player_tracks, ball_tracks)

    # Detect events (passes, interceptions, rebounds, shot attempts)
    passes, interceptions, rebounds, shot_attempts = event_detector.detect_all(ball_aquisition, player_assignment, ball_tracks)

    # Calculate stints and point differentials
    num_players = len(player_assignment[0])  # Total players
    stints = []  # List of stints (teammates, opponents, point differential)

    for frame_num, shot in enumerate(shot_attempts):
        if shot:  # If a shot attempt occurred
            team = player_assignment[frame_num][shot["player_id"]]
            point_diff = 2 if shot["made"] else -2  # Example scoring logic
            teammates = [p for p, t in player_assignment[frame_num].items() if t == team]
            opponents = [p for p, t in player_assignment[frame_num].items() if t != team]
            stints.append((teammates, opponents, point_diff))

    # Prepare RAPM data
    num_stints = len(stints)
    X = np.zeros((num_stints, num_players))
    y = np.zeros(num_stints)

    for i, (teammates, opponents, point_diff) in enumerate(stints):
        for t in teammates:
            X[i, t] = 1
        for o in opponents:
            X[i, o] = -1
        y[i] = point_diff

    # Apply Ridge regression
    alpha = 1.0  # Regularization strength
    model = Ridge(alpha=alpha)
    model.fit(X, y)

    # Extract coefficients (β values)
    beta = model.coef_

    # Calculate Plus-Minus (PM) values using the provided equation
    PM = np.zeros(num_players)
    for i in range(num_players):
        # Minutes/possessions played by player i
        N_i = np.sum(X[:, i] == 1)
        
        # Contribution of teammates
        teammate_contrib = 0
        for j in range(num_players):
            if j != i:
                N_ijt = np.sum((X[:, i] == 1) & (X[:, j] == 1))  # Shared stints
                teammate_contrib += N_ijt * beta[j]
        
        # Contribution of opponents
        opponent_contrib = 0
        for k in range(num_players):
            N_iko = np.sum((X[:, i] == 1) & (X[:, k] == -1))  # Opponent stints
            opponent_contrib += N_iko * beta[k]
        
        # Calculate PM for player i
        PM[i] = N_i * beta[i] + teammate_contrib - opponent_contrib

    # Output RAPM-style values and Plus-Minus values
    print("\nPlayer Adjusted Plus-Minus values:")
    for idx, coef in enumerate(beta):
        print(f"Player {idx}: RAPM Coefficient (β): {coef:.3f}, PM: {PM[idx]:.3f}")

# Example usage
calculate_rapm(
    video_path="input_videos/video_3.mp4",
    player_tracker_path="models/player_detector.pt",
    ball_tracker_path="models/ball_detector.pt",
    stub_path="stubs"
)