import torch
import scipy as sp


################################
# Testing
################################

class Lam_network(torch.nn.Module):
    """docstring for Lam_network"""
    def __init__(self, arg):
        super(Lam_network, self).__init__()
        self.model = torch.nn.Sequential(
            torch.nn.Conv1d(
                in_channels, out_channels, kernel_size,
                stride=1, padding=0, dilation=1, groups=1),
            torch.nn.MaxPool1d(
                kernel_size,
                stride=None, padding=0, dilation=1),
            torch.nn.Linear(),
            torch.nn.Linear(),
            torch.nn.Sigmoid()
        )


    def forward(self, x):
        return None


lam_net = Lam_network()

def update_probs(probs, logits):
    print(probs.shape)
    print(logits)
    return probs

def sim(probs, elements):
    # 1 if elements was already predicted else 0
    return elements.clamp(0, 1)


def select_set(seq_predictions, logits, p=.1):
    # seq_predictions: tensor(|A|, voc_size)
    stop = lambda c, m: m[c] >= 1 + p * m.sum()


    # The memory is shared accross sequences for one decoding step
    # Memory counts the number of time a token was predicted
    # memory: tensor(voc_size)
    memory = torch.zeros(seq_predictions.shape[-1])


    output = set()

    # For every partial sequence next step
    for i, (seq_prob, seq_logits) in enumerate(zip(seq_predictions, logits)):
        # Get one new token
        prediction = seq_prob
        cand = prediction.argmax().item()

        # Storing prediction now to ensure at least 1 token per sequence.
        # If every token was predicted then memory is full and no more token
        #  can be predicted.
        output |= {(i, cand)}

        # Keep getting new tokens
        while not stop(cand, memory):
            # Storing parent ID and token ID
            output |= {(i, cand)}
            # Updating memory
            memory[cand] += 1

            update_probs(seq_prob, seq_logits)
            # Update prediction
            prediction = seq_prob - .4 * sim(seq_prob, memory)
            cand = prediction.argmax().item()

    # Separating parent and token lists
    output = sorted(output)
    print()
    return [e[0] for e in output], [e[1] for e in output]


def decode(start_prediction, start_state, step, Y=None, max_step=6, end_tok=5):

    start_prediction = torch.tensor(start_prediction)
    if Y is not None:
        m = max(len(el) for el in Y)
        Y = [el + [end_tok] * (m - len(el) + 1) for el in Y]
        Y = torch.tensor(Y)

    # TODO: Tackle alive/dead sequences
    # These should not be decoded and no set should be associated with them
    # TODO: Integrate into AllenNLP BeamSearch
    if Y is not None:
        max_step = Y.shape[-1]
    # No batches !
    # start_prediction : tensor(1)
    # start_state : tensor(*)
    # step : prediction:(n) -> state:dict[tensor(*)] ->
    #  (prediction:(n,voc) , state:dict[tensor(*)])

    logits = [None]

    probabilities, state = step(start_prediction, start_state)
    # probabilities: tensor(1, voc_size)

    if Y is not None:
        loss = []
        mask = torch.zeros(probabilities.shape[-1]) == 1
        mask[Y[:, 0]] = True
        ma, mi = (probabilities[:, ~mask].max(-1)[0],
                  probabilities[:, mask].min(-1)[0])
        P = (ma + mi) / 2
        loss.append(((probabilities - P) ** 2).sum())

    back, prediction = select_set(probabilities, logits)
    # back: list(n). Where do the token come from.
    # prediction: list(n). Actual token.

    # backpointer is A. The set of partial sequences
    backpointers = [[p_] for p_ in prediction]
    # Update the prediction (used to predict next tokens)
    prediction = torch.tensor([b[-1] for b in backpointers])
    # Update the state (duplicate the preivous states to account for the newly
    #  created partial sequences)
    state = torch.tensor([state[b] for b in back])
    logits = [[probabilities] for b in back]

    for timestep in range(1, max_step):
        # Computing next step for every n partial sequences
        probabilities, state = step(prediction, state)
        # probabilities: tensor(n, voc_size)

        if Y is not None:
            mask = torch.zeros(probabilities.shape[-1]) == 1
            mask[Y[:, timestep]] = True
            # y_ = [e[:timestep+1].tolist() in backpointers for e in Y]
            ma, mi = (probabilities[:, ~mask].max(-1)[0],
                      probabilities[:, mask].min(-1)[0])
            P = (ma + mi) / 2
            loss.append(((probabilities - P.view(-1, 1)) ** 2).sum())

        # The number of new token per sequence is different for every partial sequence
        back, prediction = select_set(probabilities, logits)
        # Update the backpointers
        backpointers = [backpointers[b] + [p_] for b, p_ in zip(back, prediction)]

        prediction = torch.tensor([b[-1] for b in backpointers])
        state = torch.tensor([state[b] for b in back])
        logits = [logits[b] + [probabilities[b]] for b in back]

    if Y is not None:
        backpointers = (backpointers, loss)
    return backpointers


################################
# Training
################################

def compute_accuracy(Xs, Ys, **kwargs):
    acc = 0
    for x, y in zip(Xs, Ys):
        s = decode(x, torch.tensor([0]), decoder, Y=y)[0]
        acc += len(set(map(tuple, s)) & set(map(tuple, y))) / len(s)
    return acc


def compute_loss(Xs, Ys):
    losses = [decode(x, torch.tensor([0]), decoder, Y=y)[1]
              for x, y in zip(Xs, Ys)]
    return torch.tensor(losses).sum(-1).tolist()


################################
# Execute
################################

# Fake decoder function
data = torch.tensor([
    [0.3, 0.2, 0.3, 0.2, 0.4, 0.1],
    [0.4, 0.1, 0.2, 0.3, 0.3, 0.2],
    [0.1, 0.1, 0.2, 0.6, 0.3, 0.2],
    [0.1, 0.7, 0.1, 0.1, 0.2, 0.3],
    [0.2, 0.7, 0.4, 0.1, 0.1, 0.2],
    [0.1, 0.09, 0.08, 0.06, 0.07, 0.6],
])


def decoder(pred, state=0):
    return data[pred], data[pred].topk(2)[0].sum(-1)


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    import seaborn as sns
    import pandas as pd

    X = [[0], [1], [2]]
    Y = [[[2, 1, 3], [3, 2], [0, 1, 2]],
         [[0, 1, 1, 2], [3, 2, 4, 0]],
         [[2, 2]]]

    # print(compute_accuracy(X, Y))
    state = torch.tensor([0])

    print(decode(X[0], state, decoder))
