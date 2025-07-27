import cv2
import numpy as np
from PIL import Image

class LayoutSegmenter:
    def __init__(self):
        pass

    def find_horizontal_sections(self, image_path, min_gap_height=40, debug=False):
        """
        Detect large horizontal whitespace gaps (section dividers) in a webpage screenshot.
        Returns a list of y-coordinates (start, end) for each detected section.
        """
        # Load image
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        # Adaptive threshold to highlight whitespace
        thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                       cv2.THRESH_BINARY_INV, 15, 10)
        # Sum pixels horizontally
        horizontal_projection = np.sum(thresh, axis=1)
        # Normalize
        norm_proj = horizontal_projection / np.max(horizontal_projection)
        # Find long runs of low values (whitespace)
        whitespace = norm_proj < 0.15  # 0.0 = pure white, 1.0 = pure black
        # Find contiguous whitespace regions
        sections = []
        in_gap = False
        gap_start = 0
        for y, is_white in enumerate(whitespace):
            if is_white and not in_gap:
                in_gap = True
                gap_start = y
            elif not is_white and in_gap:
                in_gap = False
                gap_end = y
                if gap_end - gap_start > min_gap_height:
                    sections.append((gap_start, gap_end))
        # Add last gap if image ends in whitespace
        if in_gap and (len(whitespace) - gap_start > min_gap_height):
            sections.append((gap_start, len(whitespace)))
        # Now, use these gaps to define section boundaries
        boundaries = [0]
        for start, end in sections:
            boundaries.append(end)
        if boundaries[-1] != img.shape[0]:
            boundaries.append(img.shape[0])
        # Return as list of (start_y, end_y) tuples
        section_ranges = [(boundaries[i], boundaries[i+1]) for i in range(len(boundaries)-1)]
        if debug:
            self.visualize_boundaries(img, section_ranges)
        return section_ranges

    def visualize_boundaries(self, img, section_ranges, out_path='debug_sections.png'):
        vis = img.copy()
        for start, end in section_ranges:
            cv2.rectangle(vis, (0, start), (vis.shape[1]-1, end), (0, 255, 0), 2)
        cv2.imwrite(out_path, vis)
        print(f"Saved debug visualization to {out_path}") 