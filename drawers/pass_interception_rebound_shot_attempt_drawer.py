import cv2
import numpy as np

class EventDrawer:
    """
    Draw passes, interceptions, rebounds, and detailed shot attempts on video frames.
    Shots are categorized: Made/Missed x Wide Open / Contested / Heavily Contested
    """
    def __init__(self):
        pass

    def get_stats(self, passes, interceptions, rebounds, shots):
        """
        Calculate total events per team including 6 shot categories.
        shots: list of dicts per frame {"player_id":int, "made":bool, "contest_level":0/1/2}
        """
        stats = {
            "team1": {"passes":0, "interceptions":0, "rebounds":0,
                      "shots_made":[0,0,0], "shots_missed":[0,0,0]},
            "team2": {"passes":0, "interceptions":0, "rebounds":0,
                      "shots_made":[0,0,0], "shots_missed":[0,0,0]}
        }

        for p,i,r,s in zip(passes, interceptions, rebounds, shots):
            # Passes
            if p == 1: stats["team1"]["passes"] += 1
            elif p == 2: stats["team2"]["passes"] += 1
            # Interceptions
            if i == 1: stats["team1"]["interceptions"] += 1
            elif i == 2: stats["team2"]["interceptions"] += 1
            # Rebounds
            if r == 1: stats["team1"]["rebounds"] += 1
            elif r == 2: stats["team2"]["rebounds"] += 1
            # Shots
            if s is not None:
                team = 1 if s["player_id"] % 2 == 1 else 2  # Example team assignment
                contest = s.get("contest_level",0)  # 0: wide open, 1: contested, 2: heavily contested
                if s["made"]:
                    stats[f"team{team}"]["shots_made"][contest] += 1
                else:
                    stats[f"team{team}"]["shots_missed"][contest] += 1

        return stats

    def draw(self, video_frames, passes, interceptions, rebounds, shots):
        output_frames = []
        for frame_num, frame in enumerate(video_frames):
            if frame_num == 0:
                continue
            frame_drawn = self.draw_frame(frame, frame_num, passes, interceptions, rebounds, shots)
            output_frames.append(frame_drawn)
        return output_frames

    def draw_frame(self, frame, frame_num, passes, interceptions, rebounds, shots):
        overlay = frame.copy()
        font_scale = 0.55
        font_thickness = 1

        h, w = overlay.shape[:2]
        rect_x1 = int(w * 0.16)
        rect_y1 = int(h * 0.65)
        rect_x2 = int(w * 0.57)
        rect_y2 = int(h * 0.95)
        text_x = int(w * 0.19)
        text_y_start = int(h * 0.70)
        line_height = int(h * 0.055)

        cv2.rectangle(overlay, (rect_x1, rect_y1), (rect_x2, rect_y2), (255, 255, 255), -1)
        alpha = 0.8
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

        # Stats up to current frame
        passes_t = passes[:frame_num+1]
        interceptions_t = interceptions[:frame_num+1]
        rebounds_t = rebounds[:frame_num+1]
        shots_t = shots[:frame_num+1]

        stats = self.get_stats(passes_t, interceptions_t, rebounds_t, shots_t)

        # Draw Team 1
        y = text_y_start
        cv2.putText(frame,
                    f"Team1 Passes: {stats['team1']['passes']} Interceptions: {stats['team1']['interceptions']} Rebounds: {stats['team1']['rebounds']}",
                    (text_x, y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    font_scale,
                    (0,0,0),
                    font_thickness)
        y += line_height
        cv2.putText(frame,
                    f"Shots Made (Wide/Cont/Heav): {stats['team1']['shots_made'][0]}/{stats['team1']['shots_made'][1]}/{stats['team1']['shots_made'][2]}",
                    (text_x, y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    font_scale,
                    (0,0,0),
                    font_thickness)
        y += line_height
        cv2.putText(frame,
                    f"Shots Missed (Wide/Cont/Heav): {stats['team1']['shots_missed'][0]}/{stats['team1']['shots_missed'][1]}/{stats['team1']['shots_missed'][2]}",
                    (text_x, y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    font_scale,
                    (0,0,0),
                    font_thickness)

        # Draw Team 2
        y += line_height*1.2
        cv2.putText(frame,
                    f"Team2 Passes: {stats['team2']['passes']} Interceptions: {stats['team2']['interceptions']} Rebounds: {stats['team2']['rebounds']}",
                    (text_x, y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    font_scale,
                    (0,0,0),
                    font_thickness)
        y += line_height
        cv2.putText(frame,
                    f"Shots Made (Wide/Cont/Heav): {stats['team2']['shots_made'][0]}/{stats['team2']['shots_made'][1]}/{stats['team2']['shots_made'][2]}",
                    (text_x, y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    font_scale,
                    (0,0,0),
                    font_thickness)
        y += line_height
        cv2.putText(frame,
                    f"Shots Missed (Wide/Cont/Heav): {stats['team2']['shots_missed'][0]}/{stats['team2']['shots_missed'][1]}/{stats['team2']['shots_missed'][2]}",
                    (text_x, y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    font_scale,
                    (0,0,0),
                    font_thickness)

        return frame