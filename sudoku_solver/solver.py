import io
from collections import Counter
from typing import ByteString, List

import matplotlib.pyplot as plt
import requests
import sudokum
from minio_handler import MinioHandler


class SudokuSolvePipeline:
    def __init__(
        self,
        minio_host: str,
        minio_access_key: str,
        minio_secret_key: str,
        solve_bucket_name: str,
        api_endpoint: str,
        api_file_endpoint: str,
    ) -> None:
        self.solve_bucket_name = solve_bucket_name
        self.minio_client = MinioHandler(minio_host, minio_access_key, minio_secret_key)
        self.api_endpoint = api_endpoint
        self.api_file_endpoint = api_file_endpoint

    @staticmethod
    def validate_sudoku(sudoku: List[List[int]]) -> bool:
        """Проверка на то, что нам был отправлен валидный судоку для решения"""
        # Проверяем что это 9 строк по 9 символов
        if len(sudoku) != 9:
            print(f"Not 9 rows")
            return False
        for row in sudoku:
            if len(row) != 9:
                print("Not 9 elements in a row")
                return False

        # Проверяем символы внутри
        all_elements = set()
        for row in sudoku:
            all_elements = all_elements.union(row)
        not_valid_values = all_elements.difference({i for i in range(10)})
        if len(not_valid_values) > 0:
            print(f"Not valid values - {not_valid_values}")
            return False

        # Проверяем что они корректно расставлены (нет внутри квадранта 3x3 повторений и нет повторений в строках)
        for row in sudoku:
            row_counter = Counter(row)
            row_counter.pop(0)
            if len(row_counter) == 0:
                continue
            if row_counter.most_common()[0][1] > 1:
                print("Not valid - row duplicate")
                return False
        for col_idx in range(len(sudoku)):
            col = [row[col_idx] for row in sudoku]
            col_counter = Counter(col)
            col_counter.pop(0)
            if len(col_counter) == 0:
                continue
            if col_counter.most_common()[0][1] > 1:
                print("Not valid - col duplicate")
                return False
        return True

    @staticmethod
    def solve(sudoku: List[List[int]]):
        """Вместо решения используем либу, так как цель проекта - сетевое взаимодействие, а не алгоритмы"""
        try:
            flag, res = sudokum.solve(sudoku, max_try=3)
            assert flag == True, "Либа не смогла решить судоку"
        except Exception as err:
            print(err)
            res = None
        finally:
            return res

    @staticmethod
    def draw_it(solved: List[List[int]]) -> ByteString:
        fig, ax = plt.subplots(figsize=(9, 9))
        ax.set_xlim(0, 9)
        ax.set_ylim(0, 9)
        ax.set_axis_off()
        plt.gca().invert_yaxis()

        for row_idx, sudoku_row in enumerate(solved):
            for col_idx, value in enumerate(sudoku_row):
                ax.annotate(xy=(col_idx + 0.5, row_idx + 0.75), text=str(value), ha="center", fontsize=36)

        for i in range(1, 9):
            if i % 3 == 0:
                ax.axhline(i, lw=5)
                ax.axvline(i, lw=5)
            else:
                ax.axhline(i)
                ax.axvline(i)

        buffer = io.BytesIO()
        fig.savefig(buffer, format="png")
        plt.close(fig)
        buffer.seek(0)
        return buffer

    def do_pipeline(self, chat_id: str, file_minio_name: str, sudoku: List[List[int]], **__):
        is_valid = self.validate_sudoku(sudoku)
        if is_valid:
            solved = self.solve(sudoku)
            if solved:
                image = self.draw_it(solved)
                self.minio_client.save_in_bucket(self.solve_bucket_name, f"{file_minio_name}.png", image)
                requests.get(self.api_file_endpoint, params={"chat_id": chat_id, "object_id": f"{file_minio_name}.png"})
            else:
                requests.get(self.api_endpoint, params={"chat_id": chat_id, "text": "Didn't found how to solve it"})
        else:
            requests.get(self.api_endpoint, params={"chat_id": chat_id, "text": "Not valid sudoku"})
