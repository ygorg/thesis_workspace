import torch
import scipy as sp


################################
# Testing
################################


def sim(probs, elements):
    # 1 if elements was already predicted else 0
    return elements.clamp(0, 1)


def select_set(prediction_og, lam=-.4, p=.1):
    # prediction_og: tensor(|A|, voc_size)
    stop = lambda c, m: m[c] >= 1 + p * m.sum()

    # The memory is shared for one decoding step
    # memory: tensor(voc_size)
    memory = torch.zeros(prediction_og.shape[-1])

    output = set()

    # For every partial sequence next step
    for i, prev_seq in enumerate(prediction_og):
        # Get one new token
        prediction = prev_seq
        cand = prediction.argmax().item()
        output |= {(i, cand)}
        # Keep getting new tokens
        while not stop(cand, memory):
            output |= {(i, cand)}
            # Updating memory
            memory[cand] += 1

            # Update prediction
            prediction = prev_seq + lam * sim(prev_seq, memory)
            cand = prediction.argmax().item()

    output = sorted(output)
    return [e[0] for e in output], [e[1] for e in output]


def decode(start_prediction, start_state, step, max_step=6):
    # TODO: Tackle alive/dead sequences
    # These should not be decoded and no set should be associated with them
    # TODO: How to train the lambdas ?
    # TODO: Integrate into AllenNLP BeamSearch
    lam = [-.2, -.1, -.05, -.025, -.0, 0.]
    # No batches !
    # start_prediction : tensor(1)
    # start_state : tensor(*)
    # step : prediction:(n) -> state:dict[tensor(*)] ->
    #  (prediction:(n,voc) , state:dict[tensor(*)])

    probabilities, state = step(start_prediction, start_state)
    # probabilities: tensor(1, voc_size)

    back, prediction = select_set(probabilities, lam=lam[0])
    # back: list(n). Where do the token come from.
    # prediction: list(n). Actual token.

    # backpointer is A. The set of partial sequences
    backpointers = [[None, p_] for p_ in prediction]
    # Update the prediction (used to predict next tokens)
    prediction = torch.tensor([b[-1] for b in backpointers])
    # Update the state (duplicate the preivous states to account for the newly
    #  created partial sequences)
    state = torch.tensor([state[b] for b in back])

    for timestep in range(1, max_step):
        # Computing next step for every n partial sequences
        probabilities, state = step(prediction, state)
        # probabilities: tensor(n, voc_size)
        # The number of new token per sequence is different for every partial sequence
        back, prediction = select_set(probabilities, lam=lam[timestep])
        # Update the backpointers
        backpointers = [backpointers[b] + [p_] for b, p_ in zip(back, prediction)]

        prediction = torch.tensor([b[-1] for b in backpointers])
        state = torch.tensor([state[b] for b in back])
    return backpointers


################################
# Training
################################

def compute_accuracy(Xs, Ys, lam, **kwargs):
    acc = 0
    for x, y in zip(Xs, Ys):
        s = select_set(x, lam=lam, **kwargs)
        acc += (s.clip(0, 1) == y).sum() / len(x)
    return acc


def compute_loss(Xs, Ys, lam):
    def loss(x, y, lam):
        P = (x[~y].max() + x[y].min()) / 2
        return sum((p - P - lam) ** 2 for p in x)
    return sum(loss(x, y, lam) for x, y in zip(Xs, Ys))


def compute_lambda(Xs, Ys, **kwargs):
    res = sp.optimize.minimize_scalar(
        lambda lam: 1 - compute_loss(Xs, Ys, lam),
        method='Bounded', bounds=[-1, 0])
    return res['x']


################################
# Execute
################################

data = torch.tensor([
    [0.3, 0.2, 0.3, 0.2, 0.4],
    [0.4, 0.1, 0.2, 0.3, 0.3],
    [0.1, 0.1, 0.2, 0.6, 0.3],
    [0.1, 0.7, 0.1, 0.1, 0.2],
    [0.2, 0.7, 0.4, 0.1, 0.1],
])


def decoder(pred, state=0):
    return data[pred], data[pred].topk(2)[0].sum(-1)


if __name__ == '__main__':
    decode(torch.tensor([0]), torch.tensor([0]), decoder)
