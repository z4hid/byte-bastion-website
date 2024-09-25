from PIL import Image


class ImageConverter:
    def create_rgb_image(self, file_path):
        """
        Convert a binary file to an RGB image.

        Args:
            file_path (str): Path to the binary file.

        Returns:
            PIL.Image: RGB image.
        """
        with open(file_path, 'rb') as f:
            binary_data = f.read()

        rgb_data = []
        for i in range(0, len(binary_data), 3):
            r = binary_data[i] if i < len(binary_data) else 0
            g = binary_data[i+1] if i+1 < len(binary_data) else 0
            b = binary_data[i+2] if i+2 < len(binary_data) else 0
            rgb_data.append((r, g, b))

        size = self.get_size(len(rgb_data))
        image = Image.new('RGB', size)
        image.putdata(rgb_data)
        return image

    def get_size(self, data_length):
        """
        Determine the appropriate image size based on the data length.
        """
        if data_length < 10240:
            width = 32
        elif 10240 <= data_length <= 10240 * 3:
            width = 64
        elif 10240 * 3 < data_length <= 10240 * 6:
            width = 128
        elif 10240 * 6 < data_length <= 10240 * 10:
            width = 256
        elif 10240 * 10 < data_length <= 10240 * 20:
            width = 384
        elif 10240 * 20 < data_length <= 10240 * 50:
            width = 512
        elif 10240 * 50 < data_length <= 10240 * 100:
            width = 768
        elif 1024 * 100 < data_length <= 1024 * 150:
            width = 1024
        else:
            width = 2048
        
        height = (data_length // width) + 1
        return (width, height)
