import io
from typing import List, Tuple

import cv2
import numpy as np
from PIL import Image


class ImageParser:
    """Класс пытается найти судоку на изображении и разрезать его по каждой клетке"""

    def __init__(self, image_bytes):
        self.original_image = np.asarray(Image.open(io.BytesIO(image_bytes)))
        self.sudoku_image = None
        self.squares = None
        self.cells = None

    @staticmethod
    def make_image_binary(pixels: np.ndarray, threshold: int) -> np.ndarray:
        """Преобразовать в монохромное изображение + обрезать по порогу"""
        monochrome = cv2.cvtColor(pixels, cv2.COLOR_BGR2GRAY)
        color_thresh_func = np.vectorize(lambda x: 255 if x > threshold else 0)
        return color_thresh_func(monochrome)

    @staticmethod
    def get_filled_lines(pixels: np.ndarray, axis):
        """Поиск полностью заграшенных вертикальных/горизонтальных линий (границы судоку)"""
        line_fill_thresh = int((pixels.sum(axis=axis).min() + 3000) * 1.05)
        return np.where(pixels.sum(axis=axis) < line_fill_thresh)[0]

    def crop_sudoku(self):
        """Находим на скриншоте судоку и обрезаем его"""
        # Зная интерфейс приложения обрезаем сверху и снизу по 150 символов (сверху черная полоса оповещений и реклама внизу)
        binary_image = self.make_image_binary(self.original_image[150:-150, :], 100)
        filled_rows = self.get_filled_lines(binary_image, axis=1)
        top_line = filled_rows.min() + 150
        bot_line = filled_rows.max() + 150
        cropped_image = binary_image[top_line : bot_line + 1, :]

        filled_columns = self.get_filled_lines(cropped_image, axis=0)
        left_line = filled_columns.min()
        right_line = filled_columns.max()
        self.sudoku_image = self.original_image[top_line : bot_line + 1, left_line : right_line + 1, :]

    @staticmethod
    def group_line_to_intervals(indexes_with_black_pixels: np.ndarray) -> List[Tuple[int, int]]:
        """Ищем интервалы - линии разделения на поле судоку"""
        grouped_intervals = []
        start = None
        previous = None
        for idx in indexes_with_black_pixels:
            if start is None:
                start = idx
                previous = idx
                continue
            if idx - 1 == previous:
                previous = idx
            else:
                grouped_intervals.append((start, previous))
                start = idx
                previous = idx
        else:
            grouped_intervals.append((start, previous))
        return grouped_intervals

    def split_sudoku_to_squares(self):
        """Разбиваем судоку на 9 основных квадратов по линиям разделения"""
        binary_sudoku = self.make_image_binary(self.sudoku_image, 150)
        grouped_row_lines = self.group_line_to_intervals(self.get_filled_lines(binary_sudoku, axis=1))
        grouped_col_lines = self.group_line_to_intervals(self.get_filled_lines(binary_sudoku, axis=0))

        assert len(grouped_row_lines) == len(grouped_col_lines) == 4, "Sudoku not found on image"

        squares = []
        for row_idx in range(len(grouped_row_lines) - 1):
            row = []
            row_start = grouped_row_lines[row_idx][1] + 1
            row_end = grouped_row_lines[row_idx + 1][0]
            for col_idx in range(len(grouped_col_lines) - 1):
                col_start = grouped_col_lines[col_idx][1] + 1
                col_end = grouped_col_lines[col_idx + 1][0]
                row.append(binary_sudoku[row_start:row_end, col_start:col_end])
            squares.append(row)

        # Проверяем что квадраты равны по размеру
        sizes = [s.size for s in row for row in squares]
        assert min(sizes) / max(sizes) > 0.9, "Sudoku not found on image"
        self.squares = squares

    @staticmethod
    def split_square_to_cells(square: np.ndarray):
        """Разбиваем квадрат из судоку на 9 ячеек по размерам этого квадрата"""
        line_diff_mapper = {0: 6, 1: 7, 2: 5}
        rows_size, cols_size = square.shape
        cell_row_size = int((rows_size - line_diff_mapper[rows_size % 3]) / 3)
        cell_col_size = int((cols_size - line_diff_mapper[cols_size % 3]) / 3)

        cells = []
        for row in range(3):
            cells_row = []
            for col in range(3):
                cell_row_start = row * (cell_row_size + 2) + 2
                cell_row_end = cell_row_start + cell_row_size - 2
                cell_col_start = col * (cell_col_size + 2) + 2
                cell_col_end = cell_col_start + cell_col_size - 2
                cell = square[cell_row_start:cell_row_end, cell_col_start:cell_col_end]
                cells_row.append(cell)
            cells.append(cells_row)
        return cells

    def split_squares_to_cells(self):
        cells = []
        for row_of_squares in self.squares:
            row_of_cells_0 = []
            row_of_cells_1 = []
            row_of_cells_2 = []
            for square in row_of_squares:
                square_cells = self.split_square_to_cells(square)
                row_of_cells_0.extend(square_cells[0])
                row_of_cells_1.extend(square_cells[1])
                row_of_cells_2.extend(square_cells[2])
            cells.extend([row_of_cells_0, row_of_cells_1, row_of_cells_2])
        self.cells = cells
        self.digit_mask = [[cell.sum() / cell.size < 250 for cell in row] for row in self.cells]

    @staticmethod
    def resize_and_norm_image(cell_image: np.ndarray) -> np.ndarray:
        resized = cv2.resize(cell_image.astype(np.float64), dsize=(20, 20), interpolation=cv2.INTER_AREA)
        return resized

    def do_parse(self):
        self.crop_sudoku()
        self.split_sudoku_to_squares()
        self.split_squares_to_cells()
