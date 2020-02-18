import numpy as np
import scipy as sp


################################
# Testing
################################


def sim(probs, elements):
    # 1 if elements was already predicted else 0
    return elements.clip(0, 1)


def select_set(prediction_og, lam=-.4, p=0.):
    stop = lambda c, m: m[c] >= 1 + p * m.sum()
    memory = np.zeros(len(prediction_og))

    # Choose first elements
    prediction = prediction_og
    cand = prediction.argmax()
    while not stop(cand, memory):
        # Updating memory
        memory[cand] += 1

        # Update prediction
        prediction = prediction_og + lam * sim(prediction_og, memory)
        cand = prediction.argmax()
    return memory


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

if __name__ == '__main__':
    import seaborn as sns
    import matplotlib.pyplot as plt

    Xs = np.array([[0.4, 0.27, 0.23, 0.1]])
    Ys = np.array([[True, True, False, False]])

    # Plot accuracy and loss according to lambda (from -1 to 1)
    losses = {x: (compute_accuracy(Xs, Ys, x), compute_loss(Xs, Ys, x))
              for x in np.arange(-1., 1., 0.05)}
    sns.scatterplot(sorted(losses), [losses[k][0] for k in sorted(losses)])
    sns.scatterplot(sorted(losses), [losses[k][1] for k in sorted(losses)])
    plt.show()
