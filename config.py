"""Configurações globais do Puzzle Cam."""

# Resolução lógica usada para mapear o cursor da câmera para o puzzle.
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720

# Configuração do puzzle.
PUZZLE_ROWS = 3
PUZZLE_COLS = 3

# Distância normalizada entre polegar e indicador para considerar PINÇA.
# A distância é calculada em coordenadas normalizadas do MediaPipe.
PINCH_THRESHOLD = 0.08

# Confiança mínima do MediaPipe.
HAND_DETECTION_CONFIDENCE = 0.5
HAND_TRACKING_CONFIDENCE = 0.5

# Apenas uma mão é necessária para o controle.
MAX_NUM_HANDS = 1

# Suavização simples do cursor. 0 = sem suavização; 1 = imóvel.
CURSOR_SMOOTHING = 0.20
