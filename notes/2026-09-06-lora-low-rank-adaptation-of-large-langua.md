# Reading Notes: LoRA: Low-Rank Adaptation of Large Language Models

- **Date:** 2026-09-06
- **Source:** [https://arxiv.org/abs/2106.09685](https://arxiv.org/abs/2106.09685)
- **Category / Tags:** #lora #finetuning #llm #peft

## Summary & Core Contribution
An important paradigm of natural language processing consists of large-scale pre-training on general domain data and adaptation to particular tasks or domains. As we pre-train larger models, full fine-tuning becomes increasingly expensive. We propose Low-Rank Adaptation, or LoRA, which freezes the pre-trained model weights and injects trainable rank decomposition matrices into each layer of the Transformer architecture.

*(Unedited)*

## Key Highlights
- Focuses on practical ML/DL performance and architecture considerations.
- Method addresses efficiency, scalability, and generalization.

## Open Questions & Future Reads
- How does this approach compare on out-of-distribution benchmarks?
- Potential applicability to multi-modal and agentic workflows.
