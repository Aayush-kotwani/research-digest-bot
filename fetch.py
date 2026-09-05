import feedparser
import logging
import time
from typing import List, Dict

logger = logging.getLogger(__name__)

# Combine categories into a single query to strictly respect arXiv's rate limits
ARXIV_COMBINED_URL = (
    "https://export.arxiv.org/api/query?"
    "search_query=cat:cs.LG+OR+cat:cs.AI+OR+cat:cs.CV+OR+cat:cs.CL"
    "&sortBy=submittedDate&sortOrder=desc&max_results=40"
)

RSS_FEEDS = [
    "http://googleresearch.blogspot.com/atom.xml",
    "https://bair.berkeley.edu/blog/feed.xml",
    "https://huggingface.co/blog/feed.xml",
    "https://www.deepmind.com/blog/rss.xml",
    "https://openai.com/news/rss/",
]

FALLBACK_CLASSIC_PAPERS = [
    {
        "id": "seminal_attention_1706.03762",
        "title": "Attention Is All You Need",
        "url": "https://arxiv.org/abs/1706.03762",
        "abstract": "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks that include an encoder and a decoder. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely.",
        "tags": ["transformers", "attention", "nlp", "deeplearning"],
        "source": "Classic ML Reading"
    },
    {
        "id": "seminal_resnet_1512.03385",
        "title": "Deep Residual Learning for Image Recognition",
        "url": "https://arxiv.org/abs/1512.03385",
        "abstract": "Deeper neural networks are more difficult to train. We present a residual learning framework to ease the training of networks that are substantially deeper than those used previously. We explicitly reformulate the layers as learning residual functions with reference to the layer inputs, instead of learning unreferenced functions.",
        "tags": ["computervision", "resnet", "deeplearning"],
        "source": "Classic ML Reading"
    },
    {
        "id": "seminal_lora_2106.09685",
        "title": "LoRA: Low-Rank Adaptation of Large Language Models",
        "url": "https://arxiv.org/abs/2106.09685",
        "abstract": "An important paradigm of natural language processing consists of large-scale pre-training on general domain data and adaptation to particular tasks or domains. As we pre-train larger models, full fine-tuning becomes increasingly expensive. We propose Low-Rank Adaptation, or LoRA, which freezes the pre-trained model weights and injects trainable rank decomposition matrices into each layer of the Transformer architecture.",
        "tags": ["lora", "finetuning", "llm", "peft"],
        "source": "Classic ML Reading"
    },
    {
        "id": "seminal_flashattn_2205.14135",
        "title": "FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness",
        "url": "https://arxiv.org/abs/2205.14135",
        "abstract": "Transformers are slow and memory-hungry on long sequences, since the time and memory complexity of self-attention are quadratic in sequence length. We propose FlashAttention, an IO-aware exact attention algorithm that uses tiling to reduce the number of memory reads/writes between GPU high bandwidth memory (HBM) and GPU on-chip SRAM.",
        "tags": ["flashattention", "efficiency", "gpu", "transformers"],
        "source": "Classic ML Reading"
    },
    {
        "id": "seminal_ddpm_2006.11239",
        "title": "Denoising Diffusion Probabilistic Models",
        "url": "https://arxiv.org/abs/2006.11239",
        "abstract": "We present high quality image synthesis results using diffusion probabilistic models, a class of latent variable models inspired by considerations from nonequilibrium thermodynamics. Our best results are obtained by training on a weighted variational bound designed according to a novel connection between diffusion models and denoising score matching with Langevin dynamics.",
        "tags": ["diffusion", "generativeai", "computervision"],
        "source": "Classic ML Reading"
    },
    {
        "id": "seminal_dpo_2305.18290",
        "title": "Direct Preference Optimization: Your Language Model is Secretly a Reward Model",
        "url": "https://arxiv.org/abs/2305.18290",
        "abstract": "While large-scale unsupervised language models learn broad world knowledge, steering their behavior to adhere to user preferences requires reinforcement learning from human feedback (RLHF). We introduce Direct Preference Optimization (DPO), an algorithm to implicitly optimize the same objective as existing RLHF algorithms but without training a separate reward model or sampling during fine-tuning.",
        "tags": ["dpo", "rlhf", "alignment", "llm"],
        "source": "Classic ML Reading"
    },
    {
        "id": "seminal_adam_1412.6980",
        "title": "Adam: A Method for Stochastic Optimization",
        "url": "https://arxiv.org/abs/1412.6980",
        "abstract": "We introduce Adam, an algorithm for first-order gradient-based optimization of stochastic objective functions, based on adaptive estimates of lower-order moments. The method is straightforward to implement, is computationally efficient, has little memory requirements, is invariant to diagonal rescaling of the gradients, and is well suited for problems that are large in terms of data and/or parameters.",
        "tags": ["optimization", "adam", "gradientdescent"],
        "source": "Classic ML Reading"
    },
    {
        "id": "seminal_bert_1810.04805",
        "title": "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",
        "url": "https://arxiv.org/abs/1810.04805",
        "abstract": "We introduce a new language representation model called BERT, which stands for Bidirectional Encoder Representations from Transformers. Unlike recent language representation models, BERT is designed to pre-train deep bidirectional representations from unlabeled text by jointly conditioning on both left and right context in all layers.",
        "tags": ["bert", "transformers", "nlp"],
        "source": "Classic ML Reading"
    },
    {
        "id": "seminal_vit_2010.11929",
        "title": "An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale",
        "url": "https://arxiv.org/abs/2010.11929",
        "abstract": "While the Transformer architecture has become the de-facto standard for natural language processing tasks, its applications to computer vision remain limited. We show that reliance on CNNs is not necessary and a pure transformer applied directly to sequences of image patches can perform very well on image classification tasks.",
        "tags": ["vit", "computervision", "transformers"],
        "source": "Classic ML Reading"
    },
    {
        "id": "seminal_gan_1406.2661",
        "title": "Generative Adversarial Nets",
        "url": "https://arxiv.org/abs/1406.2661",
        "abstract": "We propose a new framework for estimating generative models via an adversarial process, in which we simultaneously train two models: a generative model G that captures the data distribution, and a discriminative model D that estimates the probability that a sample came from the training data rather than G.",
        "tags": ["gan", "generativemodels", "deeplearning"],
        "source": "Classic ML Reading"
    }
]

def fetch_arxiv() -> List[Dict]:
    results = []
    seen_ids = set()
    logger.info("Fetching arXiv papers (combined query)...")
    try:
        feed = feedparser.parse(ARXIV_COMBINED_URL)
        if getattr(feed, 'bozo', 0) and not feed.entries:
            logger.warning(f"arXiv feed warning/error: {getattr(feed, 'bozo_exception', 'unknown')}")

        for entry in feed.entries:
            if entry.id in seen_ids:
                continue
            seen_ids.add(entry.id)
            results.append({
                "id": entry.id,
                "title": entry.title.replace('\n', ' ').strip(),
                "url": entry.link,
                "abstract": getattr(entry, 'summary', '').replace('\n', ' ').strip(),
                "tags": [t['term'].split('.')[-1] for t in entry.tags] if 'tags' in entry else ['arxiv'],
                "source": "arXiv"
            })
    except Exception as e:
        logger.error(f"Error fetching arXiv: {e}")

    logger.info(f"Fetched {len(results)} candidate arXiv papers")
    return results

def fetch_rss() -> List[Dict]:
    results = []
    for url in RSS_FEEDS:
        logger.info(f"Fetching RSS: {url}")
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:10]:
                item_id = getattr(entry, 'id', None) or entry.link
                results.append({
                    "id": item_id,
                    "title": entry.title.replace('\n', ' ').strip(),
                    "url": entry.link,
                    "abstract": getattr(entry, 'summary', getattr(entry, 'description', '')).replace('\n', ' ').strip(),
                    "tags": ['blog', 'research'],
                    "source": feed.feed.get('title', 'Blog')
                })
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
    return results

def get_fallback_items() -> List[Dict]:
    """Returns fallback classic seminal papers when real-time feeds yield nothing new."""
    return list(FALLBACK_CLASSIC_PAPERS)

def fetch_all() -> List[Dict]:
    return fetch_arxiv() + fetch_rss()
