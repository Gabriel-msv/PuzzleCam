"""
Ponto de entrada do projeto Puzzle Cam.

Nesta primeira etapa, a aplicação contém apenas a estrutura arquitetural.
A integração completa com Panda3D será adicionada nos módulos renderer/
e interaction/ sem contaminar a lógica de visão ou do puzzle.
"""

from enum import Enum, auto


class GameState(Enum):
    """Estados globais da aplicação."""

    MENU = auto()
    CAMERA = auto()
    CAPTURING = auto()
    PLAYING = auto()
    SOLVED = auto()


def main() -> None:
    """Ponto de entrada."""
    print("Puzzle Cam - estrutura inicial")
    print("Próxima etapa: integrar Camera + HandTracker + Panda3D.")


if __name__ == "__main__":
    main()
