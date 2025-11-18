import unittest
from unittest.mock import MagicMock, patch
import sys
import os
from PIL import Image

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from image_processor import ImageProcessor
from config_manager import ConfigManager

class TestImageProcessorRefactor(unittest.TestCase):
    def setUp(self):
        self.mock_config = MagicMock(spec=ConfigManager)
        self.mock_config.getint.return_value = 20
        self.mock_config.getboolean.return_value = True
        self.mock_config.getfloat.return_value = 1.0
        self.mock_config.get.return_value = "test_value"
        
        # Mock dependencies to avoid import errors if libs are missing in test env
        with patch("image_processor.PILLOW_AVAILABLE", True), \
             patch("image_processor.GENAI_LIB_AVAILABLE", True), \
             patch("image_processor.NUMPY_AVAILABLE", True):
            self.processor = ImageProcessor(self.mock_config)

    def test_process_image_integration(self):
        # Mock the provider
        mock_provider = MagicMock()
        self.processor.gemini_provider = mock_provider
        
        # Mock response from provider
        mock_provider.process_image.return_value = [
            {
                "id": "test_id_1",
                "original_text": "Hello",
                "translated_text": "你好",
                "bbox_norm": [0.1, 0.1, 0.2, 0.2],
                "orientation": "horizontal",
                "font_size_category": "medium",
                "text_align": "left"
            }
        ]
        
        # Create dummy image
        dummy_image_path = "dummy_test_image.png"
        img = Image.new('RGB', (100, 100), color = 'red')
        img.save(dummy_image_path)
        
        try:
            # Run process_image
            original_img, blocks = self.processor.process_image(dummy_image_path)
            
            # Assertions
            self.assertIsNotNone(blocks)
            self.assertEqual(len(blocks), 1)
            self.assertEqual(blocks[0].original_text, "Hello")
            self.assertEqual(blocks[0].translated_text, "你好")
            
            # Check if pixel bbox is calculated correctly (100x100 image)
            # bbox_norm [0.1, 0.1, 0.2, 0.2] -> [10, 10, 20, 20]
            expected_bbox = [10.0, 10.0, 20.0, 20.0]
            self.assertEqual(blocks[0].bbox, expected_bbox)
            
            print("Test passed: ImageProcessor correctly integrated with provider.")
            
        finally:
            if os.path.exists(dummy_image_path):
                os.remove(dummy_image_path)

if __name__ == '__main__':
    unittest.main()
