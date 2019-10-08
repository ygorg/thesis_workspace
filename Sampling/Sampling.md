# Sampling

[insights](https://medium.com/machine-learning-at-petiteprogrammer/sampling-strategies-for-recurrent-neural-networks-9aea02a6616f)
[Nucleus Sampling](https://arxiv.org/pdf/1904.09751.pdf)
https://github.com/openai/gpt-2/commit/ac5d52295f8a1c3856ea24fb239087cc1a3d1131

Now we are using beamsearch to get multiple keyphrases out of a neural model (and also we get theoretically more probable keyphrases than with greedy decoding).

Sampling is like BeamSearch with a width of 1 but instead of choosing the Top1 element you actually choose from the probability distribution using the softmax result as the density function.

Sampling introduce randomness which means that for 2 runs, the results will differ.


Keyphrases are subjective, and vary depending on person, time, expertise, etc??...
This is why an annotation for a document will change if the annotator or the time changes.
To alleviate this problem of subjectivity for non-expert annotators **how non-subjective are professional indexers ??**, the crowdsourcing method was introduced, so the keyphrases are the common annotation of many non-expert readers. This is like bagging or something.

With BeamSearch our model is consistent because it will always annotate in the same way (given that is it not trained regularly).


1. If sampling a lot, will the most occuring keyphrases be the output of the BeamSearch ?
2. If using sampling, will the absent keyphrase be more accurate ?
3. How to create consistency using sampling ? (if 1. is false)