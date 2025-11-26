# ⛑️ YOLOv8 PPE Detection & Compliance System 🚧

**A deep learning solution using YOLOv8 for real-time Personal Protective Equipment (PPE) detection in industrial and construction environments.**

---

## ✨ Project Overview

This project implements a state-of-the-art object detection model, **YOLOv8**, to monitor safety compliance by automatically identifying both the presence and absence of essential Personal Protective Equipment (PPE) in images and video streams.

The goal is to enhance workplace safety, automate compliance checks, and minimize human error in hazard reduction.

### 🔑 Key Features
* **Real-time Detection:** High-speed inference suitable for live video streams.
* **10-Class Classification:** Detection includes both compliance (e.g., `Hardhat`, `Safety Vest`) and non-compliance (e.g., `NO-Hardhat`, `NO-Safety Vest`) classes.
* **Custom Training:** Model trained on a custom, diverse dataset tailored for industrial settings.
* **Detailed Metrics:** Comprehensive evaluation using mAP, Precision, and Recall.

---

## 🏷️ Detected Classes (10)

| Compliance Status | Class Name | Description |
| :--- | :--- | :--- |
| **✅ Compliant** | `Hardhat` | Worker wearing a hardhat. |
| | `Mask` | Worker wearing a mask. |
| | `Safety Vest` | Worker wearing a safety vest. |
| **❌ Non-Compliant** | `NO-Hardhat` | Worker without a hardhat. |
| | `NO-Mask` | Worker without a mask. |
| | `NO-Safety Vest` | Worker without a safety vest. |
| **🏗️ Environmental**| `Person` | Detection of any human. |
| | `Safety Cone` | Safety marker. |
| | `Machinery` | Industrial equipment. |
| | `Vehicle` | On-site transportation. |

---

## 📊 Dataset & Statistics

The model was trained on a custom dataset split into standard YOLO format (`train`, `valid`, `test`). Each image includes corresponding annotation files.

| Split | Images | Labels (Annotations) |
| :--- | :---: | :---: |
| **Train** | 2605 | 2605 |
| **Validation** | 114 | 114 |
| **Test** | 82 | 82 |

---

## ⚙️ Configuration & Parameters

The training environment and model behavior are managed via the central `CFG` class.

| Parameter Category | Example Parameter | Default Value | Description |
| :--- | :--- | :--- | :--- |
| **Model** | `BASE_MODEL` | `yolov8s.pt` | The base YOLOv8 architecture weights (e.g., small). |
| | `IMGSZ` | `(640, 640)` | Image size for training and inference. |
| **Training** | `EPOCHS` | `50` | Number of training iterations. |
| | `BATCH_SIZE` | `16` | Samples processed per batch. |
| | `LEARNING_RATE (LR)` | `1e-3` | Initial learning rate. |
| | `PATIENCE` | *(Auto)* | Early stopping patience to prevent overfitting. |
| **Inference** | `CONF` | `0.30` | Confidence threshold for final bounding box display. |
| | `DEVICE` | `cuda` | Hardware target for acceleration (e.g., `cuda` or `0`). |

---

## 📈 Training & Results

### Training Command

The model was trained using the Ultralytics Python API:

```python
# Assuming model is initialized (model = YOLO(CFG.BASE_MODEL_WEIGHTS))

model.train(
    data=os.path.join(CFG.OUTPUT_DIR, 'data.yaml'),
    task='detect',
    imgsz=(640, 640),
    epochs=CFG.EPOCHS,
    batch=CFG.BATCH_SIZE,
    name=f'{CFG.BASE_MODEL}_{CFG.EXP_NAME}',
    # ... other CFG parameters used ...
    device=0,
    val=True,
    amp=True 
)
```

### Final Performance Metrics

| Metric | Value | Interpretation |
| :--- | :---: | :--- |
| **Precision** | 0.869 | High ratio of true detections to total detections. |
| **Recall** | 0.640 | Moderate coverage of all actual objects in the dataset. |
| **mAP@50** | 0.690 | Mean Average Precision at IoU threshold of 50%. (Good overall performance) |
| **mAP@50-95** | 0.370 | Mean Average Precision across IoU thresholds 50% to 95%. |

---

## 🖼️ Visualization & Inference

### Random Image Plotting (Validation Check)
To visualize how labels correspond to the training data:

```python
plot_random_images_from_folder(folder_path, num_images=20, seed=CFG.SEED)
```

### Running Inference on an Image
To detect objects on a specific file:

```python
results = model.predict(
    source=example_image_path,
    conf=0.30,
    device="cuda",
    imgsz=(640, 640),
    save=True,        # Save output image with boxes
    save_txt=True,    # Save text annotations
    exist_ok=True,
)
```

⚙️ Setup & Requirements
### Installation
Ensure you have Python 3.8+ installed.

```bash
pip install -r requirements.txt
```

## ⚙️ Dependencies

The primary libraries used are:
* `ultralytics` (for YOLOv8)
* `numpy`, `pandas`
* `matplotlib`, `seaborn`
* `opencv-python`
* `Pillow`, `PyYAML`

---

## 💻 Hardware

* **GPU:** NVIDIA GeForce RTX 3060 Laptop GPU (CUDA version: 12.6.77)
* **RAM:** 16GB or higher
* **CPU:** Intel Core i9 (or equivalent)

---

## 📁 Outputs & Storage

* **Prediction Results:** Saved in the `runs/detect/` directory (includes inferred images/videos).
* **Training History:** Metrics are logged as `training_log_df.csv`.
* **Sample Output:** Sample inference images and videos are found in the `outputs/` directory.

---

## ⚠️ Limitations & Future Work

### Current Limitations
* The model's performance may degrade when detecting **partially obscured or small PPE items**.
* Results are sensitive to **low-light conditions** or visually complex backgrounds not present in the training data.
* **Generalization capability** for entirely new industrial environments is limited without transfer learning or re-training.

### Next Steps & Future Work
* **Dataset Expansion:** Add more images covering diverse lighting, angles, and environmental conditions.
* **Performance Tuning:** Implement advanced techniques (e.g., TTA, model ensemble, hyperparameter search) to achieve target recall and precision levels.
* **Real-time Deployment:** Integrate the model with a platform like Streamlit or Flask for real-time industrial monitoring systems with alerting capabilities.
