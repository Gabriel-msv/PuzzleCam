# Puzzle Cam

Projeto nativo em Python para reproduzir o puzzle controlado por gestos.

## Stack

- Python
- Panda3D
- OpenCV
- MediaPipe
- NumPy

## Arquitetura

```text
puzzle_cam/
├── main.py
├── config.py
├── camera/
├── vision/
├── puzzle/
├── renderer/
└── interaction/
```

## Regra de interação

O cursor virtual usa o `INDEX_FINGER_TIP` (landmark 8).

O gesto de pinça usa a distância euclidiana 2D entre:

- `THUMB_TIP` = landmark 4
- `INDEX_FINGER_TIP` = landmark 8

Se:

```text
distance < PINCH_THRESHOLD
```

o estado de pinça é verdadeiro.

## Instalação

Recomenda-se usar uma virtualenv:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

No Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Observação

O `vision/hand_tracker.py` usa a API `mediapipe.solutions.hands`, que fornece os
21 landmarks e `HAND_CONNECTIONS`. Essa API é mantida pelo projeto como solução
legada/as-is; a lógica do projeto foi isolada para que a implementação possa
migrar para `mp.tasks.vision.HandLandmarker` posteriormente sem alterar o puzzle.
