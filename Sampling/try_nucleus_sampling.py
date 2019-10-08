import torch

probs = torch.rand((4, 5))
p = 0.9  # proportion of the probability mass
sorted_probs, a_i = probs.sort(descending=True)
p_per_ex = (probs.sum(dim=-1) * p).view(-1, 1)
sorted_cumsum_probs = sorted_probs.cumsum(dim=-1)

# Computing the first index that is >= to p
indices = torch.where(
    sorted_cumsum_probs >= p_per_ex,
    torch.arange(probs.shape[-1], 0, -1).expand(*probs.shape).type(torch.float),
    torch.zeros_like(probs)
).max(-1)[1]
indices = torch.arange(probs.shape[-1]).expand(*probs.shape) <= indices.view(-1, 1)
indices = indices.type(torch.float)

torch.arange(0,4).view(-1, 1).expand(4, 5)*5

indices = torch.gather(indices, 1, a_i)
probs[indices==0] = 0
torch.multinomial(sorted_probs, 1)