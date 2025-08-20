class ReboundDetector:
    def detect_rebounds(self, ball_tracks, ball_aquisition):
        """
        Returns a list of rebounds with frame index and player_id.
        """
        rebounds = []
        previous_possession = None

        for frame_idx, possession_info in enumerate(ball_aquisition):
            current_possession = possession_info['player_id'] if possession_info else None

            # Rebound happens if previous possession is None (ball free) and current is someone
            if previous_possession is None and current_possession is not None:
                rebounds.append({
                    'frame': frame_idx,
                    'player_id': current_possession
                })

            previous_possession = current_possession

        return rebounds
