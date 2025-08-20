import cv2
import numpy as np

class ReboundDrawer:
    """
    A class responsible for calculating and drawing rebound statistics
    on a sequence of video frames.
    """
    def __init__(self):
        pass

    def get_stats(self, rebounds):
        """
        Calculate the number of rebounds for Team 1 and Team 2.

        Args:
            rebounds (list): A list of integers representing rebound events at each frame.
                (1 represents a rebound by Team 1, 2 represents a rebound by Team 2, 0 represents no rebound.)

        Returns:
            tuple: (team1_rebounds, team2_rebounds)
        """
        team1_rebounds = []
        team2_rebounds = []

        for frame_num, rebound_frame in enumerate(rebounds):
            if rebound_frame == 1:
                team1_rebounds.append(frame_num)
            elif rebound_frame == 2:
                team2_rebounds.append(frame_num)

        return len(team1_rebounds), len(team2_rebounds)

    def draw(self, video_frames, rebounds):
        """
        Draw rebound statistics on a list of video frames.

        Args:
            video_frames (list): A list of frames (as NumPy arrays).
            rebounds (list): A list of integers representing rebound events at each frame.
                (1 = Team 1 rebound, 2 = Team 2 rebound, 0 = no rebound)

        Returns:
            list: Frames with rebound stats drawn on them.
        """
        output_video_frames = []
        for frame_num, frame in enumerate(video_frames):
            if frame_num == 0:
                continue
            
            frame_drawn = self.draw_frame(frame, frame_num, rebounds)
            output_video_frames.append(frame_drawn)
        return output_video_frames
    
    def draw_frame(self, frame, frame_num, rebounds):
        """
        Draw a semi-transparent overlay of rebound counts on a single frame.

        Args:
            frame (numpy.ndarray): The current video frame.
            frame_num (int): Frame index.
            rebounds (list): A list of rebound events up to this frame.

        Returns:
            numpy.ndarray: Frame with overlay.
        """
        overlay = frame.copy()
        font_scale = 0.7
        font_thickness=2

        # Rectangle placement
        frame_height, frame_width = overlay.shape[:2]
        rect_x1 = int(frame_width * 0.16) 
        rect_y1 = int(frame_height * 0.75)
        rect_x2 = int(frame_width * 0.55)  
        rect_y2 = int(frame_height * 0.90)
        
        text_x = int(frame_width * 0.19)  
        text_y1 = int(frame_height * 0.80)  
        text_y2 = int(frame_height * 0.88)

        cv2.rectangle(overlay, (rect_x1, rect_y1), (rect_x2, rect_y2), (255,255,255), -1)
        alpha = 0.8
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

        # Get stats till now
        rebounds_till_frame = rebounds[:frame_num+1]
        team1_rebounds, team2_rebounds = self.get_stats(rebounds_till_frame)

        # Draw text
        cv2.putText(
            frame, 
            f"Team 1 - Rebounds: {team1_rebounds}",
            (text_x, text_y1), 
            cv2.FONT_HERSHEY_SIMPLEX, 
            font_scale, 
            (0,0,0), 
            font_thickness
        )
        
        cv2.putText(
            frame, 
            f"Team 2 - Rebounds: {team2_rebounds}",
            (text_x, text_y2), 
            cv2.FONT_HERSHEY_SIMPLEX, 
            font_scale, 
            (0,0,0), 
            font_thickness
        )

        return frame
