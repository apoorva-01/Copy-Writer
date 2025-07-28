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

    def detect_visual_blocks(self, image_path, min_contour_area=0.001):
        """
        Detects major visual blocks in an image using contour detection.

        Args:
            image_path (str): The path to the image file.
            min_contour_area (float): The minimum area of a contour to be considered a block,
                                      as a fraction of the total image area.

        Returns:
            list: A list of dictionaries, where each dictionary represents a detected
                  block with its bounding box coordinates (x, y, width, height).
        """
        try:
            image = cv2.imread(image_path)
            if image is None:
                print(f"❌ Error: Could not read image at {image_path}")
                return []

            img_height, img_width, _ = image.shape
            total_area = img_width * img_height

            # 1. Preprocessing for layout detection
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            # Invert the image because we are looking for dark text on light backgrounds
            # and contours are found on white objects.
            gray = 255 - gray
            
            # Apply blur to reduce noise and small details
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)

            # Use adaptive thresholding to handle different lighting conditions
            thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                           cv2.THRESH_BINARY_INV, 11, 4)

            # 2. Dilate to merge text into blocks
            # Use larger kernels to connect separated parts of a section, like columns
            # in a footer.
            rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 5))
            dilated = cv2.dilate(thresh, rect_kernel, iterations=3)

            # 3. Find contours
            contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # 4. Filter contours to get block-level elements
            detected_blocks = []
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                # Filter out very small or very large (full-image) contours
                if cv2.contourArea(contour) > total_area * min_contour_area and cv2.contourArea(contour) < total_area * 0.95:
                    detected_blocks.append({'x': x, 'y': y, 'width': w, 'height': h})
            
            # Sort blocks by their top-y coordinate
            detected_blocks.sort(key=lambda block: block['y'])

            print(f"✅ LayoutSegmenter detected {len(detected_blocks)} visual blocks.")
            return detected_blocks

        except Exception as e:
            print(f"❌ Error in LayoutSegmenter: {e}")
            return [] 