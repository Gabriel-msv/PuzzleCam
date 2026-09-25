"""
Lógica pura do puzzle de imagem.

Este módulo não conhece:
- Panda3D;
- OpenCV;
- MediaPipe;
- webcam;
- janela;
- eventos de interface.

Ele trabalha somente com geometria, peças e estado do jogo.

A posição do cursor é expressa no mesmo sistema normalizado [0, 1] usado
pelo MediaPipe:
    (0, 0) = canto superior esquerdo
    (1, 1) = canto inferior direito
"""

from __future__ import annotations

from dataclasses import dataclass
from random import Random
from typing import List, Optional, Sequence, Tuple


@dataclass(frozen=True, slots=True)
class Rect:
    """Retângulo normalizado usado para colisão."""

    x: float
    y: float
    width: float
    height: float

    @property
    def right(self) -> float:
        return self.x + self.width

    @property
    def bottom(self) -> float:
        return self.y + self.height

    def contains(self, point: Tuple[float, float]) -> bool:
        """Retorna True se o ponto estiver dentro do retângulo."""
        px, py = point
        return (
            self.x <= px < self.right
            and self.y <= py < self.bottom
        )


@dataclass(slots=True)
class PuzzlePiece:
    """
    Uma peça do puzzle.

    `correct_index` nunca muda.
    `current_index` representa a posição ocupada atualmente.
    """

    piece_id: int
    correct_index: int
    current_index: int
    source_rect: Rect
    board_rect: Rect

    @property
    def is_correct(self) -> bool:
        return self.current_index == self.correct_index


class Puzzle:
    """
    Estado e regras do puzzle.

    Por padrão:
        3 x 3 = 9 peças.

    O puzzle usa uma permutação dos índices:
        [0, 1, 2, 3, 4, 5, 6, 7, 8]

    O índice é sempre:
        index = row * cols + col
    """

    def __init__(
        self,
        rows: int = 3,
        cols: int = 3,
        *,
        board_rect: Rect = Rect(0.20, 0.10, 0.60, 0.80),
        seed: Optional[int] = None,
    ) -> None:
        if rows < 2 or cols < 2:
            raise ValueError("O puzzle precisa ter pelo menos 2x2.")

        if board_rect.width <= 0 or board_rect.height <= 0:
            raise ValueError("board_rect precisa possuir largura e altura positivas.")

        if board_rect.x < 0 or board_rect.y < 0:
            raise ValueError("board_rect não pode começar fora do espaço normalizado.")

        if board_rect.right > 1 or board_rect.bottom > 1:
            raise ValueError("board_rect precisa estar dentro de [0, 1].")

        self.rows = rows
        self.cols = cols
        self.board_rect = board_rect
        self._rng = Random(seed)

        self._piece_width = board_rect.width / cols
        self._piece_height = board_rect.height / rows

        self._pieces: List[PuzzlePiece] = []
        self._dragged_piece_id: Optional[int] = None

        self.reset()

    @property
    def size(self) -> int:
        return self.rows * self.cols

    @property
    def pieces(self) -> Tuple[PuzzlePiece, ...]:
        """Snapshot imutável da coleção de peças."""
        return tuple(self._pieces)

    @property
    def dragged_piece_id(self) -> Optional[int]:
        return self._dragged_piece_id

    @staticmethod
    def _index_to_row_col(index: int, cols: int) -> Tuple[int, int]:
        return divmod(index, cols)

    def _board_rect_for_index(self, index: int) -> Rect:
        row, col = self._index_to_row_col(index, self.cols)

        return Rect(
            x=self.board_rect.x + col * self._piece_width,
            y=self.board_rect.y + row * self._piece_height,
            width=self._piece_width,
            height=self._piece_height,
        )

    def _source_rect_for_index(self, index: int) -> Rect:
        """
        Retângulo da imagem original correspondente à peça.

        Aqui o espaço também é normalizado, permitindo que o renderer
        transforme isso em pixels/UVs/texturas depois.
        """
        row, col = self._index_to_row_col(index, self.cols)

        return Rect(
            x=col / self.cols,
            y=row / self.rows,
            width=1.0 / self.cols,
            height=1.0 / self.rows,
        )

    def reset(self) -> None:
        """Cria o puzzle novamente em estado resolvido."""
        self._pieces.clear()
        self._dragged_piece_id = None

        for index in range(self.size):
            self._pieces.append(
                PuzzlePiece(
                    piece_id=index,
                    correct_index=index,
                    current_index=index,
                    source_rect=self._source_rect_for_index(index),
                    board_rect=self._board_rect_for_index(index),
                )
            )

    def shuffle(self, *, min_displaced: int = 2) -> None:
        """
        Embaralha as peças.

        A operação sempre termina em uma configuração diferente da solução.
        `min_displaced` define quantas peças, no mínimo, devem estar fora
        da posição correta.
        """
        if min_displaced < 1:
            raise ValueError("min_displaced deve ser >= 1.")

        if min_displaced > self.size:
            raise ValueError("min_displaced não pode ser maior que o número de peças.")

        indices = list(range(self.size))

        # Gera uma permutação e evita uma configuração com poucas alterações.
        for _ in range(1000):
            self._rng.shuffle(indices)
            displaced = sum(
                current != correct
                for current, correct in enumerate(indices)
            )

            if displaced >= min_displaced:
                break
        else:
            # Fallback determinístico para casos extremos.
            indices = list(range(self.size))
            indices[0], indices[1] = indices[1], indices[0]

        # `indices[position] = piece_id`.
        for position, piece_id in enumerate(indices):
            piece = self._pieces[piece_id]
            piece.current_index = position
            piece.board_rect = self._board_rect_for_index(position)

        self._dragged_piece_id = None

    def piece_at(self, cursor: Tuple[float, float]) -> Optional[PuzzlePiece]:
        """
        Retorna a peça cuja área ocupa o cursor.

        Complexidade: O(n), o que é irrelevante para um puzzle pequeno.
        """
        if len(cursor) != 2:
            raise ValueError("cursor precisa ser (x, y).")

        x, y = cursor
        if not (0.0 <= x <= 1.0 and 0.0 <= y <= 1.0):
            return None

        # Percorremos em ordem reversa para que, no futuro, uma peça arrastada
        # possa ser considerada visualmente acima das demais.
        for piece in reversed(self._pieces):
            if piece.board_rect.contains(cursor):
                return piece

        return None

    def piece_by_id(self, piece_id: int) -> PuzzlePiece:
        if not 0 <= piece_id < self.size:
            raise IndexError(f"piece_id inválido: {piece_id}")

        return self._pieces[piece_id]

    def begin_drag(self, cursor: Tuple[float, float]) -> Optional[int]:
        """
        Seleciona a peça sob o cursor.

        Retorna o ID da peça selecionada ou None.
        """
        piece = self.piece_at(cursor)

        if piece is None:
            self._dragged_piece_id = None
            return None

        self._dragged_piece_id = piece.piece_id
        return piece.piece_id

    def cancel_drag(self) -> None:
        """Cancela o arraste sem modificar o puzzle."""
        self._dragged_piece_id = None

    def release_drag(self, cursor: Tuple[float, float]) -> bool:
        """
        Solta a peça atualmente arrastada.

        Se houver outra peça sob o cursor, as duas posições são trocadas.
        Retorna True se houve uma troca válida.
        """
        if self._dragged_piece_id is None:
            return False

        dragged = self.piece_by_id(self._dragged_piece_id)
        target = self.piece_at(cursor)

        try:
            if target is None or target.piece_id == dragged.piece_id:
                return False

            old_position = dragged.current_index
            target_position = target.current_index

            dragged.current_index = target_position
            target.current_index = old_position

            dragged.board_rect = self._board_rect_for_index(dragged.current_index)
            target.board_rect = self._board_rect_for_index(target.current_index)

            return True
        finally:
            self._dragged_piece_id = None

    def is_solved(self) -> bool:
        """Verifica a condição de vitória."""
        return all(piece.is_correct for piece in self._pieces)

    def correct_count(self) -> int:
        """Quantidade de peças atualmente na posição correta."""
        return sum(piece.is_correct for piece in self._pieces)

    def position_of(self, piece_id: int) -> int:
        """Retorna a posição atual de uma peça."""
        return self.piece_by_id(piece_id).current_index

    def debug_matrix(self) -> List[List[int]]:
        """
        Retorna a matriz de IDs atualmente visível no tabuleiro.

        Útil para testes automatizados.
        """
        matrix = [[-1 for _ in range(self.cols)] for _ in range(self.rows)]

        for piece in self._pieces:
            row, col = self._index_to_row_col(piece.current_index, self.cols)
            matrix[row][col] = piece.piece_id

        return matrix
