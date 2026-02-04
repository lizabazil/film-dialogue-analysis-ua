from PIL import Image, ImageDraw


class ImageUtils:
    @staticmethod
    def crop_image_with_given_coordinates(original_image_path: str, save_cropped_image_path: str,
                                          left: float, upper: float, right: float, lower: float) -> None:
        """
        Crops image with the given path and saves with given output for new image.
        """
        box = (left, upper, right, lower)
        original_image = Image.open(original_image_path)
        cropped_image = original_image.crop(box)
        cropped_image.save(save_cropped_image_path)
        return None

    @staticmethod
    def draw_bounding_box_on_the_image(bbox: list, image: Image.Image,
                                       output_image_path: str = '/home/liza/PycharmProjects/film-dialogue-analysis-ua/data/screenshots/screen_with_points.jpg') -> None:
        """
        For debugging and testing purposes.
        """
        draw = ImageDraw.Draw(image)
        x1, y1, x2, y2 = int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])
        draw.rectangle([x1, y1, x2, y2], outline="white", width=2)
        image.save(output_image_path)
        return None

    @staticmethod
    def draw_bounding_box_on_the_image_in_place(bbox: list, pil_image_object) -> None:
        draw = ImageDraw.Draw(pil_image_object)
        x1, y1, x2, y2 = int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])
        draw.rectangle([x1, y1, x2, y2], outline="white", width=2)
