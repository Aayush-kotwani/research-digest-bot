# Reading Notes: FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness

- **Date:** 2026-09-07
- **Source:** [https://arxiv.org/abs/2205.14135](https://arxiv.org/abs/2205.14135)
- **Category / Tags:** #flashattention #efficiency #gpu #transformers

## Summary & Core Contribution
Transformers are slow and memory-hungry on long sequences, since the time and memory complexity of self-attention are quadratic in sequence length. We propose FlashAttention, an IO-aware exact attention algorithm that uses tiling to reduce the number of memory reads/writes between GPU high bandwidth memory (HBM) and GPU on-chip SRAM.

*(Unedited)*

## Key Highlights
- Focuses on practical ML/DL performance and architecture considerations.
- Method addresses efficiency, scalability, and generalization.

## Open Questions & Future Reads
- How does this approach compare on out-of-distribution benchmarks?
- Potential applicability to multi-modal and agentic workflows.
