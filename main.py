import os
import argparse
from utils import read_video, save_video
from trackers import PlayerTracker, BallTracker
from team_assigner import TeamAssigner
from court_keypoint_detector import CourtKeypointDetector
from ball_aquisition import BallAquisitionDetector
from pass_interception_rebound_shot_attempt_detector import PassInterceptionReboundShotAttemptDetector
from tactical_view_converter import TacticalViewConverter
from speed_and_distance_calculator import SpeedAndDistanceCalculator
from rapm import calculate_rapm  # Import the RAPM function

from drawers import (
    PlayerTracksDrawer, 
    BallTracksDrawer,
    CourtKeypointDrawer,
    TeamBallControlDrawer,
    FrameNumberDrawer,
    EventDrawer,
    TacticalViewDrawer,
    SpeedAndDistanceDrawer
)
from configs import (
    STUBS_DEFAULT_PATH,
    PLAYER_DETECTOR_PATH,
    BALL_DETECTOR_PATH,
    COURT_KEYPOINT_DETECTOR_PATH,
    OUTPUT_VIDEO_PATH
)

def parse_args():
    parser = argparse.ArgumentParser(description='Basketball Video Analysis')
    parser.add_argument('input_video', type=str, help='Path to input video file')
    parser.add_argument('--output_video', type=str, default=OUTPUT_VIDEO_PATH, 
                        help='Path to output video file')
    parser.add_argument('--stub_path', type=str, default=STUBS_DEFAULT_PATH,
                        help='Path to stub directory')
    return parser.parse_args()

def main():
    args = parse_args()
    
    # Read video
    video_frames = read_video(args.input_video)

    # Initialize trackers and detectors
    player_tracker = PlayerTracker(PLAYER_DETECTOR_PATH)
    ball_tracker = BallTracker(BALL_DETECTOR_PATH)
    team_assigner = TeamAssigner()
    ball_aquisition_detector = BallAquisitionDetector()
    event_detector = PassInterceptionReboundShotAttemptDetector()

    # Get player and ball tracks
    player_tracks = player_tracker.get_object_tracks(video_frames, read_from_stub=True, stub_path=f"{args.stub_path}/player_track_stubs.pkl")
    ball_tracks = ball_tracker.get_object_tracks(video_frames, read_from_stub=True, stub_path=f"{args.stub_path}/ball_track_stubs.pkl")

    # Assign teams
    player_assignment = team_assigner.get_player_teams_across_frames(video_frames, player_tracks, read_from_stub=True, stub_path=f"{args.stub_path}/player_assignment_stub.pkl")

    # Detect ball possession
    ball_aquisition = ball_aquisition_detector.detect_ball_possession(player_tracks, ball_tracks)

    # Detect events (passes, interceptions, rebounds, shot attempts)
    passes, interceptions, rebounds, shot_attempts = event_detector.detect_all(ball_aquisition, player_assignment, ball_tracks)

    # Perform RAPM analysis
    print("\nRunning RAPM analysis...")
    calculate_rapm(
        video_path=args.input_video,
        player_tracker_path=PLAYER_DETECTOR_PATH,
        ball_tracker_path=BALL_DETECTOR_PATH,
        stub_path=args.stub_path
    )

if __name__ == "__main__":
    main()