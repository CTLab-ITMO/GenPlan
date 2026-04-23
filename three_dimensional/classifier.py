import torch
from transformers import pipeline

from dto.enum.wall_size_type import WallSizeType
from dto.enum.window_size_type import WindowSizeType

WINDOW_LABEL_TEXT = {
    WindowSizeType.SMALL: "small low windows, compact glazing, small window openings",
    WindowSizeType.STANDARD: "standard typical windows, regular window height, normal glazing",
    WindowSizeType.HIGH: "tall windows, floor-to-ceiling glazing, panoramic windows, large vertical openings",
}

WALL_LABEL_TEXT = {
    WallSizeType.SMALL: "low wall height, low ceilings, compact interior height",
    WallSizeType.STANDARD: "standard wall height, typical ceiling height, normal interior height",
    WallSizeType.HIGH: "high walls, tall ceilings, double-height space, two-story atrium, vaulted interior",
}


def _pick_enum(model, description: str, label_map: dict, hypothesis_template: str):
    candidate_labels = list(label_map.values())
    result = model(
        sequences=description,
        candidate_labels=candidate_labels,
        hypothesis_template=hypothesis_template,
        multi_label=False
    )
    best_label_text = result["labels"][0]
    inv = {v: k for k, v in label_map.items()}
    return inv[best_label_text]


def classify_windows_and_walls(description: str) -> (WindowSizeType, WallSizeType):
    model = pipeline(
        "zero-shot-classification",
        model="facebook/bart-large-mnli",
        device=0 if torch.cuda.is_available() else -1
    )
    windows_type = _pick_enum(
        model,
        description=description,
        label_map=WINDOW_LABEL_TEXT,
        hypothesis_template="This house description implies {}."
    )
    wall_type = _pick_enum(
        model,
        description=description,
        label_map=WALL_LABEL_TEXT,
        hypothesis_template="This house description implies {}."
    )
    return windows_type, wall_type


if __name__ == "__main__":
    text = "A contemporary villa with expansive glazing and a grand entrance."
    print(classify_windows_and_walls(text))
