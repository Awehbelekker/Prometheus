"""
HRM ACT V1 — Hierarchical Reasoning Model architecture.
Reconstructed from checkpoint to match saved weights exactly.
Architecture params from hrm_checkpoints/market_finetuned/finetune_meta.json
"""
import math
from dataclasses import dataclass, field
from typing import Optional, Tuple
import torch
import torch.nn as nn
import torch.nn.functional as F


@dataclass
class HierarchicalReasoningModel_ACTV1Config:
    vocab_size: int = 20
    hidden_size: int = 512
    num_heads: int = 8
    H_layers: int = 4
    L_layers: int = 4
    H_cycles: int = 2
    L_cycles: int = 2
    expansion: int = 3
    halt_max_steps: int = 16
    seq_len: int = 101
    rms_norm_eps: float = 1e-5
    rope_theta: float = 10000.0


@dataclass
class HierarchicalReasoningModel_ACTV1Carry:
    H: torch.Tensor
    L: torch.Tensor


class RMSNorm(nn.Module):
    def __init__(self, dim: int, eps: float = 1e-5):
        super().__init__()
        self.eps = eps
        self.weight = nn.Parameter(torch.ones(dim))

    def forward(self, x):
        norm = x.pow(2).mean(-1, keepdim=True).add(self.eps).sqrt()
        return x / norm * self.weight


class RotaryEmbedding(nn.Module):
    def __init__(self, dim: int, theta: float = 10000.0):
        super().__init__()
        inv_freq = 1.0 / (theta ** (torch.arange(0, dim, 2).float() / dim))
        self.register_buffer("inv_freq", inv_freq)

    def forward(self, seq_len: int, device):
        t = torch.arange(seq_len, device=device).float()
        freqs = torch.outer(t, self.inv_freq)
        emb = torch.cat([freqs, freqs], dim=-1)
        return emb.cos(), emb.sin()


def rotate_half(x):
    x1, x2 = x.chunk(2, dim=-1)
    return torch.cat([-x2, x1], dim=-1)


def apply_rope(q, k, cos, sin):
    cos = cos.unsqueeze(0).unsqueeze(0)
    sin = sin.unsqueeze(0).unsqueeze(0)
    q = q * cos + rotate_half(q) * sin
    k = k * cos + rotate_half(k) * sin
    return q, k


class Attention(nn.Module):
    def __init__(self, hidden_size: int, num_heads: int):
        super().__init__()
        self.num_heads = num_heads
        self.head_dim = hidden_size // num_heads
        self.qkv_proj = nn.Linear(hidden_size, 3 * hidden_size, bias=False)
        self.o_proj = nn.Linear(hidden_size, hidden_size, bias=False)
        self.rope = RotaryEmbedding(self.head_dim)

    def forward(self, x):
        B, T, C = x.shape
        qkv = self.qkv_proj(x)
        q, k, v = qkv.chunk(3, dim=-1)
        q = q.view(B, T, self.num_heads, self.head_dim).transpose(1, 2)
        k = k.view(B, T, self.num_heads, self.head_dim).transpose(1, 2)
        v = v.view(B, T, self.num_heads, self.head_dim).transpose(1, 2)
        cos, sin = self.rope(T, x.device)
        q, k = apply_rope(q, k, cos, sin)
        scale = math.sqrt(self.head_dim)
        attn = torch.matmul(q, k.transpose(-2, -1)) / scale
        attn = F.softmax(attn, dim=-1)
        out = torch.matmul(attn, v)
        out = out.transpose(1, 2).contiguous().view(B, T, C)
        return self.o_proj(out)


class MLP(nn.Module):
    def __init__(self, hidden_size: int, expansion: int = 4):
        super().__init__()
        ffn = int(hidden_size) * int(expansion)
        self.gate_up_proj = nn.Linear(hidden_size, ffn * 2, bias=False)
        self.down_proj = nn.Linear(ffn, hidden_size, bias=False)

    def forward(self, x):
        gate_up = self.gate_up_proj(x)
        gate, up = gate_up.chunk(2, dim=-1)
        return self.down_proj(F.silu(gate) * up)


class TransformerLayer(nn.Module):
    def __init__(self, hidden_size: int, num_heads: int, expansion: int, eps: float):
        super().__init__()
        self.self_attn = Attention(hidden_size, num_heads)
        self.mlp = MLP(hidden_size, expansion)

    def forward(self, x):
        x = x + self.self_attn(x)
        x = x + self.mlp(x)
        return x


class TransformerStack(nn.Module):
    def __init__(self, num_layers: int, hidden_size: int, num_heads: int,
                 expansion: int, eps: float):
        super().__init__()
        self.layers = nn.ModuleList([
            TransformerLayer(hidden_size, num_heads, expansion, eps)
            for _ in range(num_layers)
        ])

    def forward(self, x):
        for layer in self.layers:
            x = layer(x)
        return x


class EmbeddingTable(nn.Module):
    """Matches checkpoint key: inner.embed_tokens.embedding_weight"""
    def __init__(self, vocab_size: int, hidden_size: int):
        super().__init__()
        self.embedding_weight = nn.Parameter(torch.randn(vocab_size, hidden_size))

    def forward(self, tokens):
        return F.embedding(tokens, self.embedding_weight)


class PuzzleEmbedding(nn.Module):
    """Matches checkpoint key: inner.puzzle_emb.weights — positional table [500, 512]"""
    def __init__(self, hidden_size: int, max_len: int = 500):
        super().__init__()
        self.weights = nn.Parameter(torch.randn(max_len, hidden_size))

    def forward(self, x):
        T = x.size(1)
        return x + self.weights[:T].unsqueeze(0)


class HRMInner(nn.Module):
    def __init__(self, cfg: HierarchicalReasoningModel_ACTV1Config):
        super().__init__()
        self.cfg = cfg
        self.H_init = nn.Parameter(torch.randn(cfg.hidden_size))
        self.L_init = nn.Parameter(torch.randn(cfg.hidden_size))
        self.embed_tokens = EmbeddingTable(cfg.vocab_size, cfg.hidden_size)
        self.puzzle_emb = PuzzleEmbedding(cfg.hidden_size)
        self.H_level = TransformerStack(cfg.H_layers, cfg.hidden_size,
                                        cfg.num_heads, cfg.expansion, cfg.rms_norm_eps)
        self.L_level = TransformerStack(cfg.L_layers, cfg.hidden_size,
                                        cfg.num_heads, cfg.expansion, cfg.rms_norm_eps)
        self.lm_head = nn.Linear(cfg.hidden_size, cfg.vocab_size, bias=False)
        self.q_head = nn.Linear(cfg.hidden_size, 2)

    def forward(self, tokens: torch.Tensor, carry: Optional[HierarchicalReasoningModel_ACTV1Carry] = None):
        B, T = tokens.shape
        x = self.embed_tokens(tokens)
        x = self.puzzle_emb(x)

        if carry is None:
            H = self.H_init.unsqueeze(0).unsqueeze(0).expand(B, 1, -1)
            L = self.L_init.unsqueeze(0).unsqueeze(0).expand(B, 1, -1)
        else:
            H = carry.H
            L = carry.L

        for _ in range(self.cfg.H_cycles):
            H = self.H_level(torch.cat([H, x], dim=1))[:, :1, :]

        for _ in range(self.cfg.L_cycles):
            L = self.L_level(torch.cat([H, x], dim=1))[:, 1:, :]

        logits = self.lm_head(L)
        q_val = self.q_head(H.squeeze(1))
        new_carry = HierarchicalReasoningModel_ACTV1Carry(H=H, L=L)
        return logits, q_val, new_carry


class HierarchicalReasoningModel_ACTV1(nn.Module):
    def __init__(self, cfg: HierarchicalReasoningModel_ACTV1Config):
        super().__init__()
        self.cfg = cfg
        self.inner = HRMInner(cfg)

    def forward(self, tokens: torch.Tensor,
                carry: Optional[HierarchicalReasoningModel_ACTV1Carry] = None):
        return self.inner(tokens, carry)

    @torch.no_grad()
    def predict(self, tokens: torch.Tensor, steps: int = 4):
        """Run multi-step ACT inference, return final logits."""
        carry = None
        logits = None
        for _ in range(steps):
            logits, q_val, carry = self.forward(tokens, carry)
        return logits, q_val
