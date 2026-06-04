import os


class FileUtils:
    @staticmethod
    def delete_file(file_path: str) -> None:
        """
        Simple implementation for deleting the file. In case of exception (for example, such file does not exist,
        it does not raise an exception, but simply pring to the console.
        Args:
            file_path (str): Path to the file to be deleted.
        Returns:
            None
        """
        file_path = os.path.abspath(file_path)
        try:
            os.remove(file_path)
        except OSError as e:
            print(f"Error while deleting the file {file_path}: {e}")
        return None
