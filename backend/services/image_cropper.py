import os
from PIL import Image
import base64
from io import BytesIO

class ImageCropper:
    def __init__(self):
        self.crop_folder = 'uploads/crops'
        # Ensure crop directory exists
        os.makedirs(self.crop_folder, exist_ok=True)
    
    def validate_and_adjust_coordinates(self, bounding_box, img_width, img_height):
        """
        Validate and adjust bounding box coordinates for better accuracy
        
        Args:
            bounding_box: Dict with x, y, width, height as percentages
            img_width: Image width in pixels
            img_height: Image height in pixels
            
        Returns:
            Adjusted bounding box coordinates
        """
        # Ensure all values are within 0-100 range
        x = max(0, min(100, bounding_box.get('x', 0)))
        y = max(0, min(100, bounding_box.get('y', 0)))
        width = max(1, min(100 - x, bounding_box.get('width', 100)))
        height = max(1, min(100 - y, bounding_box.get('height', 100)))
        
        # Convert to pixels for validation
        x_px = int((x / 100) * img_width)
        y_px = int((y / 100) * img_height)
        width_px = int((width / 100) * img_width)
        height_px = int((height / 100) * img_height)
        
        # Ensure minimum viable crop size (at least 50x50 pixels)
        min_size = 50
        if width_px < min_size:
            width_px = min(min_size, img_width - x_px)
            width = (width_px / img_width) * 100
            
        if height_px < min_size:
            height_px = min(min_size, img_height - y_px)
            height = (height_px / img_height) * 100
        
        # Adjust if coordinates go beyond image bounds
        if x_px + width_px > img_width:
            width_px = img_width - x_px
            width = (width_px / img_width) * 100
            
        if y_px + height_px > img_height:
            height_px = img_height - y_px
            height = (height_px / img_height) * 100
        
        return {
            'x': x,
            'y': y,
            'width': width,
            'height': height,
            'x_px': x_px,
            'y_px': y_px,
            'width_px': width_px,
            'height_px': height_px
        }

    def crop_section(self, image_path, section_id, bounding_box):
        """
        Crop a section from the main image based on bounding box coordinates
        
        Args:
            image_path: Path to the original image
            section_id: Unique identifier for the section
            bounding_box: Dict with x, y, width, height as percentages (0-100)
            
        Returns:
            Path to the cropped image file
        """
        try:
            # Open the original image
            with Image.open(image_path) as img:
                # Get image dimensions
                img_width, img_height = img.size
                
                # Validate and adjust coordinates
                adjusted_coords = self.validate_and_adjust_coordinates(bounding_box, img_width, img_height)
                
                x_px = adjusted_coords['x_px']
                y_px = adjusted_coords['y_px']
                width_px = adjusted_coords['width_px']
                height_px = adjusted_coords['height_px']
                
                # print(f"🎯 Cropping {section_id}: Original coords {bounding_box}")
                # print(f"   Adjusted to: x={x_px}, y={y_px}, w={width_px}, h={height_px}")
                
                # Crop the image
                cropped = img.crop((x_px, y_px, x_px + width_px, y_px + height_px))
                
                # Generate filename for the cropped section
                base_filename = os.path.splitext(os.path.basename(image_path))[0]
                crop_filename = f"{base_filename}_{section_id}.png"
                crop_path = os.path.join(self.crop_folder, crop_filename)
                
                # Save the cropped image with some optimization
                cropped.save(crop_path, 'PNG', optimize=True)
                
                return crop_path
                
        except Exception as e:
            print(f"❌ Error cropping section {section_id}: {str(e)}")
            return None
    
    def crop_all_sections(self, image_path, sections):
        """
        Crop all sections from an image
        
        Args:
            image_path: Path to the original image
            sections: List of section objects with bounding_box data
            
        Returns:
            Dict mapping section_id to cropped image path
        """
        crop_paths = {}
        
        for section in sections:
            if 'bounding_box' in section:
                crop_path = self.crop_section(
                    image_path, 
                    section['id'], 
                    section['bounding_box']
                )
                if crop_path:
                    crop_paths[section['id']] = crop_path
        
        return crop_paths
    
    def get_section_image_base64(self, crop_path):
        """
        Convert cropped image to base64 for frontend display
        
        Args:
            crop_path: Path to the cropped image
            
        Returns:
            Base64 encoded image string
        """
        try:
            with open(crop_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            print(f"Error encoding image {crop_path}: {str(e)}")
            return None
    
    def cleanup_crops(self, base_filename):
        """
        Clean up cropped images for a specific upload
        
        Args:
            base_filename: Base filename of the original upload
        """
        try:
            for filename in os.listdir(self.crop_folder):
                if filename.startswith(base_filename):
                    os.remove(os.path.join(self.crop_folder, filename))
        except Exception as e:
            print(f"Error cleaning up crops: {str(e)}") 