# Task 2: Medical Fine-tuning with Quantization and Low Rank Adaptation via Unsloth in Google Colab

## Overview

This project implements a **QLoRA-based medical fine-tuning workflow** using **Unsloth** in Google Colab.

The objective was to adapt a Llama-based language model to a domain-specific medical question-answering dataset using **4-bit quantization and Low Rank Adaptation (LoRA)**. The workflow includes dataset preparation, conversational formatting, tokenization, 4-bit model loading, LoRA adapter configuration, supervised fine-tuning, GPU memory monitoring, adapter saving, and inference on a new medical query.

> **Note:** This project is intended for educational and research purposes. The model's responses should not be treated as professional medical diagnosis or medical advice.

---

## Task Objective

The task required implementing an efficient PEFT/QLoRA workflow that:

- Loads a domain-specific medical dataset.
- Uses a Llama-based language model.
- Applies 4-bit quantization.
- Configures Low Rank Adaptation (LoRA).
- Performs tokenization and conversational formatting.
- Executes epoch-based supervised fine-tuning.
- Monitors GPU memory and training performance.
- Saves the fine-tuned LoRA adapter.
- Tests the fine-tuned model on a new medical query.

The workflow was implemented in **Google Colab using Unsloth**.

---

## Technologies Used

| Technology | Purpose |
|---|---|
| Google Colab | Cloud notebook environment |
| NVIDIA Tesla T4 | GPU for model loading, training and inference |
| Python | Notebook code and scripting |
| Unsloth | Efficient model loading, LoRA setup and fine-tuning |
| Hugging Face Transformers | Model and tokenizer functionality |
| Hugging Face Datasets | Dataset loading and processing |
| TRL | Supervised Fine-Tuning |
| PEFT / LoRA | Parameter-efficient fine-tuning |
| BitsAndBytes | 4-bit quantization |
| PyTorch | Deep learning framework |

---

## Model

The base model used in this project was:

```text
unsloth/Meta-Llama-3.1-8B-Instruct-bnb-4bit
```

The model was loaded using **4-bit quantization**.

### Why 4-bit Quantization?

Quantization stores model weights at a lower numerical precision, significantly reducing GPU memory requirements. This made it practical to fine-tune an 8-billion-parameter model on the **15 GB Tesla T4 GPU** available in Google Colab.

---

## QLoRA Approach

This project uses **QLoRA**, which combines:

1. A frozen 4-bit quantized base model.
2. Trainable LoRA adapter matrices.

Instead of updating all 8 billion model parameters, only a small fraction of parameters is trained.

### LoRA Configuration

| Parameter | Value |
|---|---|
| LoRA Rank (`r`) | 16 |
| LoRA Alpha | 16 |
| LoRA Dropout | 0 |
| Bias | None |
| Gradient Checkpointing | Unsloth |
| Trainable Parameters | 41,943,040 |
| Total Parameters | 8,072,204,288 |
| Trainable Percentage | **0.5196% (~0.52%)** |

LoRA was applied to:

```text
q_proj
k_proj
v_proj
o_proj
gate_proj
up_proj
down_proj
```

Only **0.52% of the total model parameters** were trainable while the majority of the base model remained frozen.

---

## Dataset

The project uses the following medical question-answering dataset:

```text
prithvi1029/medquad-medical-qa
```

The original dataset contains **16,407 medical Q&A examples** with the following fields:

- `qtype`
- `Question`
- `Answer`

For this project, a subset of **2,000 examples** was selected after shuffling with a fixed seed.

### Dataset Split

| Split | Examples |
|---|---:|
| Training | 1,800 |
| Testing / Validation | 200 |
| Total Selected | 2,000 |

---

## Data Formatting and Tokenization

Each medical question-answer pair was converted into a conversational structure containing:

- System message
- User question
- Assistant answer

The Llama chat template was applied through the tokenizer so that the examples matched the format expected by the Llama 3.1 Instruct model.

The maximum sequence length was set to:

```text
1024 tokens
```

Tokenization was performed through the SFT training pipeline.

---

## Fine-Tuning Configuration

Supervised Fine-Tuning (SFT) was performed using **TRL and Unsloth**.

| Parameter | Value |
|---|---|
| Training Method | Supervised Fine-Tuning (SFT) |
| Epochs | 2 |
| Per-device Batch Size | 1 |
| Gradient Accumulation Steps | 4 |
| Effective Batch Size | 4 |
| Learning Rate | 2e-4 |
| Maximum Sequence Length | 1024 |
| Optimizer | AdamW 8-bit |
| Precision | FP16 |
| Gradient Checkpointing | Enabled |
| Total Training Steps | 900 |

---

## GPU and Memory Monitoring

Training was performed on an **NVIDIA Tesla T4 GPU with 15 GB VRAM** in Google Colab.

GPU availability and memory usage were verified using:

```bash
nvidia-smi
```

Before model loading, the GPU showed:

```text
Tesla T4
15,360 MiB total memory
0 MiB used
```

The project used several memory-saving techniques:

- 4-bit quantization
- LoRA / QLoRA
- Gradient checkpointing
- Unsloth memory optimizations
- 8-bit optimizer

These techniques allowed the 8B parameter model to be fine-tuned on the available T4 GPU.

---

## Training

The model was trained on **1,800 medical examples for 2 epochs**.

Because the batch size was 1 and gradient accumulation was set to 4, the effective batch size was 4.

The training completed successfully:

```text
900 / 900 steps
Epoch 2 / 2
```

Training runtime was approximately:

```text
1 hour 30 minutes
```

### Training and Validation Loss

The validation loss improved during training:

| Step | Training Loss | Validation Loss |
|---:|---:|---:|
| 100 | 0.940659 | 0.933890 |
| 200 | 0.856099 | 0.892896 |
| 300 | 0.857027 | 0.873361 |
| 400 | 0.893673 | 0.863150 |
| 500 | 0.696510 | 0.872430 |
| 600 | 0.792169 | 0.862224 |
| 700 | 0.662208 | 0.855932 |
| 800 | 0.781651 | 0.849666 |
| 900 | 0.664847 | **0.849969** |

The final training loss was:

```text
0.664847
```

The final validation loss was:

```text
0.849969
```

Overall, validation loss decreased from approximately **0.934 to 0.850** during training.

---

## Fine-tuned Adapter

After training, the LoRA adapter and tokenizer were saved using `save_pretrained()`.

The output directory was:

```text
medical-qlora-final/
```

The saved adapter contains files including:

```text
adapter_model.safetensors
adapter_config.json
tokenizer.json
tokenizer_config.json
chat_template.jinja
README.md
```

The main trained LoRA weights are stored in:

```text
adapter_model.safetensors
```

Only the LoRA adapter was saved rather than a complete merged 8B model, keeping the fine-tuned output considerably smaller.

---

## Model Testing / Inference

After training, the model was switched to inference mode using Unsloth.

The fine-tuned model was tested with the following new medical query:

> **What are the common symptoms of asthma?**

The model generated a relevant response including:

- Wheezing
- Coughing
- Chest tightness
- Shortness of breath / trouble breathing

This demonstrated that the fine-tuned model could generate a relevant response to a new medical question.

---

## Complete Workflow

The complete workflow can be summarized as:

```text
Medical Dataset
       ↓
Data Formatting
       ↓
Tokenization
       ↓
4-bit Quantized Llama 3.1 8B
       ↓
LoRA / QLoRA Adapter Setup
       ↓
Supervised Fine-Tuning
       ↓
GPU & Memory Monitoring
       ↓
Training / Validation Loss
       ↓
Save LoRA Adapter
       ↓
New Medical Query
       ↓
Model Response
```

---

## Project Structure

```text
Task-02-Medical-QLoRA-Unsloth/
│
├── Task_2_Medical_FineTuning_QLoRA_Unsloth.ipynb
├── README.md
└── .gitignore
```

The trained adapter directory `medical-qlora-final/` is not included in the GitHub repository because model weight files are large binary files and are excluded through `.gitignore`.

---

## Results

The required Task 2 components were successfully implemented:

| Requirement | Status |
|---|---|
| Medical dataset | ✅ Completed |
| 4-bit quantization | ✅ Completed |
| Llama 3.1 8B base model | ✅ Completed |
| LoRA / QLoRA | ✅ Completed |
| Tokenization and chat formatting | ✅ Completed |
| SFT training | ✅ Completed |
| 2 epochs / 900 steps | ✅ Completed |
| GPU / memory monitoring | ✅ Completed |
| Training and validation loss tracking | ✅ Completed |
| Fine-tuned adapter saving | ✅ Completed |
| New medical query inference | ✅ Completed |

---

## Key Learning Outcomes

This project demonstrates practical experience with:

- 4-bit model quantization.
- QLoRA fine-tuning.
- Low Rank Adaptation (LoRA).
- Parameter-Efficient Fine-Tuning (PEFT).
- Memory-efficient training using Unsloth.
- Supervised Fine-Tuning with TRL.
- Medical domain adaptation.
- GPU memory monitoring in Google Colab.
- Saving and using LoRA adapters.
- Testing a fine-tuned language model on unseen medical queries.

---

## Limitations

This project was conducted as an educational fine-tuning experiment using a **2,000-example subset** of the MedQuAD dataset.

The model has not been evaluated as a clinical diagnostic system, and the inference examples are not a substitute for professional medical evaluation.

Medical outputs generated by the model should therefore be treated as educational/research outputs only.

---

