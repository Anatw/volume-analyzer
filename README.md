# Volume Analyzer

A preprocessing tool that converts audio recordings into servo movement instructions for use in animatronic systems like [Samuel the Raven](https://github.com/Anatw/samuel_the_raven). It transforms audio files (e.g., raven calls) into time-synchronized binary sequences, where `1` indicates a servo should move (e.g., mouth open) and `0` means no movement.

This tool allows the creation of multiple motion maps per audio file using different clustering thresholds, enabling randomized selection at runtime for more natural and expressive behavior.

---

## What It Does

- Loads MP3 audio using [Librosa](https://librosa.org/)
- Computes RMS energy to measure loudness over time
- Applies thresholding to detect meaningful sound events
- Groups events into "clusters" representing vocalizations
- Converts clusters into binary open/close movement lists
- Outputs multiple maps per file for varied expressiveness
- (Optional) Generates development graphs to visualize audio features

---

## Installation

```bash
git clone https://github.com/Anatw/volume-analyzer.git
cd volume-analyzer
pip install .
```

---

## Basic Usage

```python
from volume_analyzer import generate_clusters_for_servo_usage

clusters = generate_clusters_for_servo_usage(
    directory="raven_sounds",
    thresholds=[10, 70, 150],  # or use default
    print_clusters_details=False
)
```

This will return a nested dictionary structure:

```python
{
  "head_pat5.mp3": {
    10: [0, 0, 1, 1, ..., 0],
    70: [0, 1, 1, 1, ..., 0],
    150: [...],
  }
}
```

Each list contains `1` and `0` values—one per RMS frame.

---

## Key Functions

### `analysed_normalized_rms_dict(...)`

- Loads and analyzes MP3 audio
- Returns normalized RMS energy values per file

### `exceeding_indexes_clusters(...)`

- Applies thresholding to RMS data
- Groups adjacent loud segments into clusters
- Supports multiple `distance_allowed_between_clusters` settings

### `generate_clusters_for_servo_usage(...)`

- Converts clusters into binary movement maps (1=open, 0=closed)
- Returns multiple maps per file with varying cluster sensitivities

---

## Developer Graphs (Optional)

You can visualize RMS, volume, and power spectrograms during development:

```python
from volume_analyzer import generate_graphs

generate_graphs(
    generate_rms=True,
    generate_power=True,
    generate_volume=True
)
```

---

## Example Output

![image](https://github.com/user-attachments/assets/bbac2ba4-a34d-441d-9fc1-a3b5f2b34c61)

---

## Used In

This tool was developed to support the animatronic character [Samuel the Raven](https://github.com/Anatw/samuel_the_raven). It helps generate realistic, dynamic movement synced to pre-recorded raven calls.

---

## License

MIT License

---

## ✍️ Author

Developed by [Anat Wax](https://github.com/Anatw)  
Part of the [Animatronic Menagerie](https://theanimatronicmenagerie.wordpress.com/)
