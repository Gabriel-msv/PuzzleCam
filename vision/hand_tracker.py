"""
Rastreamento de uma mão e detecção do gesto de pinça.

Responsabilidades deste módulo:
- receber um frame BGR do OpenCV;
- detectar até uma mão usando MediaPipe Hands;
- expor os 21 landmarks;
- fornecer a posição normalizada do INDEX_FINGER_TIP;
- calcular a distância euclidiana THUMB_TIP <-> INDEX_FINGER_TIP;
- determinar se a mão está em estado de PINÇA.

Não há dependência de Panda3D ou da lógica do puzzle aqui.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import hypot
from typing import Optional, Sequence, Tuple

import cv2
import mediapipe as mp


# Índices oficiais dos landmarks usados pelo projeto.
THUMB_TIP = 4
INDEX_FINGER_TIP = 8
LANDMARK_COUNT = 21


@dataclass(frozen=True, slots=True)
class Landmark:
    """Landmark normalizado da mão."""

    x: float
    y: float
    z: float

    def as_tuple(self) -> Tuple[float, float, float]:
        return self.x, self.y, self.z


@dataclass(frozen=True, slots=True)
class HandState:
    """
    Resultado imutável de uma análise de frame.

    Quando `detected` é False, `landmarks` e `cursor` são None.
    """

    detected: bool
    landmarks: Optional[Tuple[Landmark, ...]]
    cursor: Optional[Tuple[float, float]]
    pinch_distance: Optional[float]
    pinching: bool
    handedness: Optional[str]
    handedness_score: Optional[float]

    @classmethod
    def empty(cls) -> "HandState":
        return cls(
            detected=False,
            landmarks=None,
            cursor=None,
            pinch_distance=None,
            pinching=False,
            handedness=None,
            handedness_score=None,
        )


class HandTracker:
    """
    Wrapper isolado do MediaPipe Hands.

    O frame recebido deve estar em BGR, que é o formato padrão do OpenCV.
    O MediaPipe recebe internamente RGB.
    """

    def __init__(
        self,
        *,
        max_num_hands: int = 1,
        model_complexity: int = 0,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
        pinch_threshold: float = 0.08,
    ) -> None:
        if max_num_hands < 1:
            raise ValueError("max_num_hands deve ser >= 1.")

        if model_complexity not in (0, 1):
            raise ValueError("model_complexity deve ser 0 ou 1.")

        if not 0.0 <= min_detection_confidence <= 1.0:
            raise ValueError("min_detection_confidence deve estar entre 0 e 1.")

        if not 0.0 <= min_tracking_confidence <= 1.0:
            raise ValueError("min_tracking_confidence deve estar entre 0 e 1.")

        if pinch_threshold <= 0.0:
            raise ValueError("pinch_threshold deve ser maior que zero.")

        self.pinch_threshold = float(pinch_threshold)

        self._mp_hands = mp.solutions.hands
        self._hands = self._mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_num_hands,
            model_complexity=model_complexity,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )

    @staticmethod
    def _distance_2d(a: Landmark, b: Landmark) -> float:
        """Distância euclidiana 2D entre dois landmarks normalizados."""
        return hypot(a.x - b.x, a.y - b.y)

    @staticmethod
    def _landmarks_from_result(hand_landmarks) -> Tuple[Landmark, ...]:
        """Converte o objeto do MediaPipe para uma tupla Python independente."""
        landmarks = tuple(
            Landmark(float(point.x), float(point.y), float(point.z))
            for point in hand_landmarks.landmark
        )

        if len(landmarks) != LANDMARK_COUNT:
            raise RuntimeError(
                f"MediaPipe retornou {len(landmarks)} landmarks; "
                f"eram esperados {LANDMARK_COUNT}."
            )

        return landmarks

    def process(self, frame_bgr) -> HandState:
        """
        Processa um frame BGR.

        Retorna:
            HandState com cursor, distância da pinça e estado pinching.
        """
        if frame_bgr is None:
            raise ValueError("frame_bgr não pode ser None.")

        if not hasattr(frame_bgr, "shape") or len(frame_bgr.shape) != 3:
            raise ValueError("frame_bgr deve ser uma imagem BGR HxWxC.")

        # O MediaPipe trabalha com RGB.
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        frame_rgb.flags.writeable = False

        results = self._hands.process(frame_rgb)

        if not results.multi_hand_landmarks:
            return HandState.empty()

        # Nesta primeira versão controlamos o jogo com a primeira mão detectada.
        hand_landmarks = results.multi_hand_landmarks[0]
        landmarks = self._landmarks_from_result(hand_landmarks)

        thumb = landmarks[THUMB_TIP]
        index = landmarks[INDEX_FINGER_TIP]

        pinch_distance = self._distance_2d(thumb, index)
        pinching = pinch_distance < self.pinch_threshold

        handedness = None
        handedness_score = None

        if results.multi_handedness:
            classification = results.multi_handedness[0].classification[0]
            handedness = str(classification.label)
            handedness_score = float(classification.score)

        return HandState(
            detected=True,
            landmarks=landmarks,
            cursor=(index.x, index.y),
            pinch_distance=pinch_distance,
            pinching=pinching,
            handedness=handedness,
            handedness_score=handedness_score,
        )

    def process_with_overlay(self, frame_bgr):
        """
        Processa um frame e desenha os landmarks diretamente sobre uma cópia.

        Este método é apenas uma ferramenta de depuração. O estado retornado
        continua sendo o `HandState`, que é a interface usada pelo restante
        do projeto.
        """
        if frame_bgr is None:
            raise ValueError("frame_bgr não pode ser None.")

        if not hasattr(frame_bgr, "shape") or len(frame_bgr.shape) != 3:
            raise ValueError("frame_bgr deve ser uma imagem BGR HxWxC.")

        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        results = self._hands.process(frame_rgb)

        # Para manter uma única execução do modelo por frame, montamos o
        # HandState a partir do mesmo resultado usado no desenho.
        if not results.multi_hand_landmarks:
            return frame_bgr.copy(), HandState.empty()

        hand_landmarks = results.multi_hand_landmarks[0]
        landmarks = self._landmarks_from_result(hand_landmarks)

        thumb = landmarks[THUMB_TIP]
        index = landmarks[INDEX_FINGER_TIP]
        pinch_distance = self._distance_2d(thumb, index)

        handedness = None
        handedness_score = None
        if results.multi_handedness:
            classification = results.multi_handedness[0].classification[0]
            handedness = str(classification.label)
            handedness_score = float(classification.score)

        state = HandState(
            detected=True,
            landmarks=landmarks,
            cursor=(index.x, index.y),
            pinch_distance=pinch_distance,
            pinching=pinch_distance < self.pinch_threshold,
            handedness=handedness,
            handedness_score=handedness_score,
        )

        output = frame_bgr.copy()
        mp_drawing = mp.solutions.drawing_utils
        mp_drawing_styles = mp.solutions.drawing_styles

        mp_drawing.draw_landmarks(
            output,
            hand_landmarks,
            self._mp_hands.HAND_CONNECTIONS,
            mp_drawing_styles.get_default_hand_landmarks_style(),
            mp_drawing_styles.get_default_hand_connections_style(),
        )

        return output, state

    def close(self) -> None:
        """Libera recursos nativos do MediaPipe."""
        self._hands.close()

    def __enter__(self) -> "HandTracker":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()
