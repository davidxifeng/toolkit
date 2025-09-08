"""
Tests for the ImageReorganizer class.
"""

import unittest
import tempfile
from pathlib import Path
from PIL import Image

from tools.image.reorganizer import ImageReorganizer


class TestImageReorganizer(unittest.TestCase):
    """Test cases for ImageReorganizer."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.reorganizer = ImageReorganizer()
        self.reorganizer.verbose = False  # Suppress output during tests
        
    def create_test_image(self, width, height, color=(255, 0, 0)):
        """Create a test image with specified dimensions and color."""
        return Image.new('RGB', (width, height), color)
    
    def test_find_best_layout_square(self):
        """Test finding best layout for perfect squares."""
        # 4 images should give 2x2
        rows, cols = self.reorganizer.find_best_layout(4)
        self.assertEqual((rows, cols), (2, 2))
        
        # 9 images should give 3x3
        rows, cols = self.reorganizer.find_best_layout(9)
        self.assertEqual((rows, cols), (3, 3))
    
    def test_find_best_layout_rectangular(self):
        """Test finding best layout for non-square numbers."""
        # 6 images should give 2x3 or 3x2
        rows, cols = self.reorganizer.find_best_layout(6)
        self.assertIn((rows, cols), [(2, 3), (3, 2)])
        
        # 8 images should give 2x4 or 4x2
        rows, cols = self.reorganizer.find_best_layout(8)
        self.assertIn((rows, cols), [(2, 4), (4, 2)])
    
    def test_find_best_layout_edge_cases(self):
        """Test edge cases for layout calculation."""
        # 0 images
        rows, cols = self.reorganizer.find_best_layout(0)
        self.assertEqual((rows, cols), (0, 0))
        
        # 1 image
        rows, cols = self.reorganizer.find_best_layout(1)
        self.assertEqual((rows, cols), (1, 1))
    
    def test_create_grid_image_basic(self):
        """Test basic grid image creation."""
        # Create a horizontal strip of 4 squares (each 50x50)
        sub_width, sub_height = 50, 50
        num_images = 4
        strip = Image.new('RGB', (sub_width * num_images, sub_height), (255, 255, 255))
        
        # Add colored squares
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
        for i, color in enumerate(colors):
            x = i * sub_width
            square = Image.new('RGB', (sub_width, sub_height), color)
            strip.paste(square, (x, 0))
        
        # Create 2x2 grid
        grid = self.reorganizer.create_grid_image(
            strip, num_images, sub_width, sub_height, 2, 2
        )
        
        # Check output dimensions
        expected_width = sub_width * 2
        expected_height = sub_height * 2
        self.assertEqual(grid.size, (expected_width, expected_height))
    
    def test_reorganize_integration(self):
        """Integration test for the complete reorganize workflow."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create a test input image (4 squares horizontally)
            sub_width, sub_height = 50, 50
            num_images = 4
            input_path = temp_path / "test_input.png"
            
            strip = Image.new('RGB', (sub_width * num_images, sub_height), (255, 255, 255))
            colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
            for i, color in enumerate(colors):
                x = i * sub_width
                square = Image.new('RGB', (sub_width, sub_height), color)
                strip.paste(square, (x, 0))
            
            strip.save(input_path)
            
            # Run reorganize
            output_path = self.reorganizer.reorganize(
                input_path=input_path,
                sub_width=sub_width
            )
            
            # Verify output file exists
            self.assertTrue(Path(output_path).exists())
            
            # Verify output image dimensions (should be 2x2 grid)
            output_img = Image.open(output_path)
            expected_size = (sub_width * 2, sub_height * 2)
            self.assertEqual(output_img.size, expected_size)


if __name__ == '__main__':
    unittest.main()