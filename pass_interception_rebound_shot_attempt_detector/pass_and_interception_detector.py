from copy import deepcopy
class PassInterceptionReboundShotAttemptDetector:
    """
    Detects passes, interceptions, rebounds, and shot attempts.
    Shot attempts are categorized as:
        Made / Missed x Wide Open / Contested / Heavily Contested
    """
    def __init__(self):
        pass

    def detect_passes(self, ball_acquisition, player_assignment):
        passes = [-1] * len(ball_acquisition)
        prev_holder = -1
        previous_frame = -1

        for frame in range(1, len(ball_acquisition)):
            if ball_acquisition[frame - 1] != -1:
                prev_holder = ball_acquisition[frame - 1]
                previous_frame = frame - 1

            current_holder = ball_acquisition[frame]

            if prev_holder != -1 and current_holder != -1 and prev_holder != current_holder:
                prev_team = player_assignment[previous_frame].get(prev_holder, -1)
                current_team = player_assignment[frame].get(current_holder, -1)

                if prev_team == current_team and prev_team != -1:
                    passes[frame] = prev_team

        return passes

    def detect_interceptions(self, ball_acquisition, player_assignment):
        interceptions = [-1] * len(ball_acquisition)
        prev_holder = -1
        previous_frame = -1

        for frame in range(1, len(ball_acquisition)):
            if ball_acquisition[frame - 1] != -1:
                prev_holder = ball_acquisition[frame - 1]
                previous_frame = frame - 1

            current_holder = ball_acquisition[frame]

            if prev_holder != -1 and current_holder != -1 and prev_holder != current_holder:
                prev_team = player_assignment[previous_frame].get(prev_holder, -1)
                current_team = player_assignment[frame].get(current_holder, -1)

                if prev_team != current_team and prev_team != -1 and current_team != -1:
                    interceptions[frame] = current_team

        return interceptions

    def detect_rebounds(self, ball_tracks, ball_acquisition):
        rebounds = [-1] * len(ball_acquisition)
        for frame in range(1, len(ball_acquisition)):
            prev_holder = ball_acquisition[frame - 1]
            current_holder = ball_acquisition[frame]

            # Rebound: ball was free and now someone has it
            if prev_holder is None and current_holder is not None:
                rebounds[frame] = current_holder
        return rebounds

    def detect_shot_attempts(self, ball_acquisition, player_assignment, shot_info_per_frame):
        """
        Detects shot attempts and categorizes them into:
        Made / Missed x Wide Open / Contested / Heavily Contested

        Args:
            ball_acquisition (list): player_id holding ball per frame
            player_assignment (list): team info per frame
            shot_info_per_frame (list): placeholder info per frame about shot attempt
                e.g., {"player_id": int, "made": True/False, "contest_level": 0/1/2}
        Returns:
            list: shot attempts per frame (dict with player_id, made, contest_level)
        """
        # Initialize list
        shots = [None] * len(ball_acquisition)

        for frame, shot_info in enumerate(shot_info_per_frame):
            if shot_info is not None:
                player_id = shot_info.get("player_id")
                made = shot_info.get("made", False)
                contest_level = shot_info.get("contest_level", 0)  # 0: wide open, 1: contested, 2: heavily contested/blocked

                # Store as dictionary
                shots[frame] = {
                    "player_id": player_id,
                    "made": made,
                    "contest_level": contest_level
                }
        return shots
