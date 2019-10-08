# Abs_Pres results

- Context : KPE for indexing blablabla
- Problem : Models are stuck at 30%
- Goal    : Finding why
- Explanation of how to reach goal :
	1. Evaluation is not suited for the task
	2. Making new models
		- Deep generative models don't generate
- Future work

## Assumption
- In order to understand whether the tasks of generating absent (abstractive) and present (extractive) keyphrases are two different task and whether they complement or restrain each other. We train a model to generate keyphrases that do not appear in the ouput and another to generate keyphrases that do appear in the input.
- [1] train a model using Graph Convolutionnal Networks that can only perform extraction and it outperforms the state of the art (DivGraphPointer F@5 36.8 vs. CopyRNN F@5 32.8).
- The basic idea would be to split the keyphrase generation into two subtask : keyphrase extraction and keyphrase generation.

## Results

| Model/F@5 | All  | Pres | Abs  |
|:--------- | ----:| ----:| ----:|
| CopySci_p | 27.4 | 32.7 |  1.2 |
| CopySci_a |  8.5 | 21.7 |  4.9 |
| CopySci   | 27.6 | 33.0 |  4.8 |

| Model/P@5 | All  | Pres | Abs  |
|:--------- | ----:| ----:| ----:|
| CopySci_p | 28.1 | 28.0 |  1.0 |
| CopySci_a |  8.5 | 20.5 |  3.7 |
| CopySci   | 28.2 | 28.2 |  3.7 |

| Model/R@5 | All  | Pres | Abs  |
|:--------- | ----:| ----:| ----:|
| CopySci_p | 29.3 | 48.5 |  1.9 |
| CopySci_a |  9.3 | 29.0 |  8.6 |
| CopySci   | 29.6 | 48.9 |  8.5 |

## Comment

* The two tasks don’t seem to help each other their scores are just combined.
* The Absent model does not generate better than the generic model. The model seem to be limiting the generation.
* The Absent model generates present keyphrases. That is linked to the fact that ”absent keyphrases” can be copied from the input (cf. Table 5).

## Future works
* Can these conclusion apply to more than this dataset ?
	- Do the same work with NYTime dataset to verify the hypothethis.
* How do the keyphrases differ between models ?
	- By watching the outputs the kp of the absent model seemed (sometime) more generic than the extracted ones (cf. Table 6).
* How to propose a model specialized in generate Absent Keyphrases ?
* Redefine the task of generating to be more abstract (cf. Table 5)


# Annex

## All metrics for every model

### All CopySci
| P@5  | R@5  | F@5  | MAP  | Model |
| 28.2 | 29.6 | 27.6 | 28.5 | All     KP20k.test.stem.json |
| 28.2 | 48.9 | 33.0 | 43.5 | Present KP20k.test.stem.json |
|  3.7 |  8.5 |  4.8 |  6.0 | Absent  KP20k.test.stem.json |

### Absent CopySci_a

La tâche consiste a prédire des séquences qui n'apparaissent pas dans l'entrée en générant un mot ou en copiant un mot de l'entrée.

| P@5  | R@5  | F@5  | MAP  | Model |
|  8.5 |  9.3 |  8.5 |  7.7 | All     KP20k.7.test.stem.json |
| 20.5 | 29.0 | 21.7 | 20.3 | Present KP20k.7.test.stem.json |
|  3.7 |  8.6 |  4.9 |  6.3 | Absent  KP20k.7.test.stem.json | 

### Present CopySci_p

| P@5  | R@5  | F@5  | MAP  | Model |
| 28.1 | 29.3 | 27.4 | 27.8 | All     KP20k.test.stem.json |
| 28.0 | 48.5 | 32.7 | 43.4 | Present KP20k.test.stem.json |
|  1.0 |  1.9 |  1.2 |  1.4 | Absent  KP20k.test.stem.json |


## Evaluating Present and Absent models for each epoch

### Absent CopySci_a

#### All
```bash
for i in $(seq 0 14)
do
	python3 util/eval_present.py -i experiments/copy_abs-b9d6765/predictions/KP20k.$i.test.jsonl.stem.json -r ~/ake-datasets/datasets/KP20k/references/test.author.stem.json -n 5
done
```

| 8.7 | 9.7 | 8.9 | 7.9 | KP20k.0.test.jsonl.stem.json |
| 8.5 | 9.4 | 8.6 | 7.7 | KP20k.1.test.jsonl.stem.json |
| 8.1 | 8.9 | 8.2 | 7.4 | KP20k.2.test.jsonl.stem.json |
| 8.6 | 9.4 | 8.7 | 7.7 | KP20k.3.test.jsonl.stem.json |
| 8.1 | 8.9 | 8.2 | 7.3 | KP20k.4.test.jsonl.stem.json |
| 8.9 | 9.7 | 8.9 | 8.0 | KP20k.5.test.jsonl.stem.json | X
| 8.7 | 9.6 | 8.8 | 7.9 | KP20k.6.test.jsonl.stem.json |
| 8.5 | 9.3 | 8.5 | 7.7 | KP20k.7.test.jsonl.stem.json | Valid X
| 8.7 | 9.5 | 8.8 | 7.8 | KP20k.8.test.jsonl.stem.json |
| 8.4 | 9.2 | 8.4 | 7.5 | KP20k.9.test.jsonl.stem.json |
| 8.4 | 9.2 | 8.4 | 7.5 | KP20k.10.test.jsonl.stem.json |
| 8.3 | 9.1 | 8.3 | 7.4 | KP20k.11.test.jsonl.stem.json |
| 8.0 | 8.8 | 8.1 | 7.1 | KP20k.12.test.jsonl.stem.json |
| 7.8 | 8.6 | 7.9 | 6.9 | KP20k.13.test.jsonl.stem.json |
| 7.7 | 8.4 | 7.7 | 6.8 | KP20k.14.test.jsonl.stem.json |

#### Absent
```bash
for i in $(seq 0 14)
do
	python3 util/eval_present.py -i experiments/copy_abs-b9d6765/predictions/KP20k.$i.test.jsonl.stem.json -r ~/ake-datasets/datasets/KP20k/references/test.author.stem.json -n 5 --absent ../data/datasets/KP20k.test.jsonl
done
```

| 2.2 | 5.0 | 2.9 | 3.6 | KP20k.0.test.jsonl.stem.json |
| 2.7 | 6.3 | 3.6 | 4.6 | KP20k.1.test.jsonl.stem.json |
| 3.2 | 7.3 | 4.2 | 5.4 | KP20k.2.test.jsonl.stem.json |
| 3.5 | 8.0 | 4.5 | 5.8 | KP20k.3.test.jsonl.stem.json |
| 3.5 | 8.1 | 4.6 | 5.9 | KP20k.4.test.jsonl.stem.json |
| 3.6 | 8.4 | 4.7 | 6.3 | KP20k.5.test.jsonl.stem.json |
| 3.7 | 8.4 | 4.8 | 6.3 | KP20k.6.test.jsonl.stem.json |
| 3.7 | 8.6 | 4.9 | 6.3 | KP20k.7.test.jsonl.stem.json | Valid X
| 3.8 | 8.7 | 5.0 | 6.4 | KP20k.8.test.jsonl.stem.json | X
| 3.7 | 8.4 | 4.8 | 6.3 | KP20k.9.test.jsonl.stem.json |
| 3.7 | 8.6 | 4.9 | 6.3 | KP20k.10.test.jsonl.stem.json |
| 3.7 | 8.7 | 4.9 | 6.3 | KP20k.11.test.jsonl.stem.json |
| 3.6 | 8.4 | 4.8 | 6.3 | KP20k.12.test.jsonl.stem.json |
| 3.6 | 8.5 | 4.8 | 6.3 | KP20k.13.test.jsonl.stem.json |
| 3.5 | 8.2 | 4.7 | 6.1 | KP20k.14.test.jsonl.stem.json |

#### Present

```bash
for i in $(seq 0 14)
do
	python3 util/eval_present.py -i experiments/copy_abs-b9d6765/predictions/KP20k.$i.test.jsonl.stem.json -r ~/ake-datasets/datasets/KP20k/references/test.author.stem.json -n 5 --present ../data/datasets/KP20k.test.jsonl
done
```

| 20.4 | 33.0 | 23.2 | 23.2 | KP20k.0.test.jsonl.stem.json | X
| 20.3 | 31.9 | 22.7 | 22.3 | KP20k.1.test.jsonl.stem.json |
| 21.2 | 30.9 | 22.8 | 21.5 | KP20k.2.test.jsonl.stem.json |
| 20.7 | 30.1 | 22.3 | 21.1 | KP20k.3.test.jsonl.stem.json |
| 21.3 | 29.3 | 22.2 | 20.6 | KP20k.4.test.jsonl.stem.json |
| 20.9 | 30.0 | 22.3 | 21.0 | KP20k.5.test.jsonl.stem.json |
| 21.1 | 29.4 | 22.1 | 20.7 | KP20k.6.test.jsonl.stem.json |
| 20.5 | 29.0 | 21.7 | 20.3 | KP20k.7.test.jsonl.stem.json | Valid X
| 21.1 | 29.1 | 22.1 | 20.6 | KP20k.8.test.jsonl.stem.json |
| 20.8 | 27.7 | 21.4 | 19.4 | KP20k.9.test.jsonl.stem.json |
| 20.8 | 27.7 | 21.3 | 19.3 | KP20k.10.test.jsonl.stem.json |
| 20.8 | 27.9 | 21.5 | 19.4 | KP20k.11.test.jsonl.stem.json |
| 20.4 | 26.0 | 20.4 | 18.3 | KP20k.12.test.jsonl.stem.json |
| 20.4 | 25.1 | 20.1 | 17.8 | KP20k.13.test.jsonl.stem.json |
| 20.2 | 24.7 | 19.8 | 17.4 | KP20k.14.test.jsonl.stem.json |

### Present CopySci_p

#### All
```bash
for i in $(seq 5 6)
do
	python3 util/eval_present.py -i experiments/copy_pres-b9d6765/predictions/KP20k.$i.test.jsonl.stem.json -r ~/ake-datasets/datasets/KP20k/references/test.author.stem.json -n 5
done
```
| 26.9 | 28.0 | 26.2 | 26.5 | KP20k.0.test.jsonl.stem.json |
| 27.8 | 29.1 | 27.2 | 27.5 | KP20k.1.test.jsonl.stem.json |
| 28.0 | 29.3 | 27.4 | 27.8 | KP20k.2.test.jsonl.stem.json |
| 28.1 | 29.6 | 27.6 | 27.9 | KP20k.3.test.jsonl.stem.json |
| 28.2 | 29.5 | 27.6 | 28.0 | KP20k.4.test.jsonl.stem.json |
| 28.1 | 29.3 | 27.4 | 27.8 | KP20k.5.test.jsonl.stem.json | X Valid
| 28.2 | 29.6 | 27.7 | 27.9 | KP20k.6.test.jsonl.stem.json |
| 28.2 | 29.7 | 27.7 | 27.9 | KP20k.7.test.jsonl.stem.json | X
| 28.1 | 29.6 | 27.6 | 27.9 | KP20k.8.test.jsonl.stem.json |
| 27.6 | 28.6 | 26.8 | 27.2 | KP20k.9.test.jsonl.stem.json |

#### Absent
```bash
for i in $(seq 5 6)
do
	python3 util/eval_present.py -i experiments/copy_pres-b9d6765/predictions/KP20k.$i.test.jsonl.stem.json -r ~/ake-datasets/datasets/KP20k/references/test.author.stem.json -n 5 --absent ../data/datasets/KP20k.test.jsonl
done
```
| 0.7 | 1.3 | 0.8 | 1.0 | KP20k.0.test.jsonl.stem.json |
| 0.9 | 1.7 | 1.0 | 1.2 | KP20k.1.test.jsonl.stem.json |
| 1.0 | 1.8 | 1.1 | 1.3 | KP20k.2.test.jsonl.stem.json |
| 1.0 | 1.9 | 1.2 | 1.4 | KP20k.3.test.jsonl.stem.json |
| 1.1 | 2.0 | 1.3 | 1.4 | KP20k.4.test.jsonl.stem.json |
| 1.0 | 1.9 | 1.2 | 1.4 | KP20k.5.test.jsonl.stem.json | X Valid
| 1.1 | 2.0 | 1.3 | 1.5 | KP20k.6.test.jsonl.stem.json |
| 1.1 | 2.0 | 1.3 | 1.4 | KP20k.7.test.jsonl.stem.json |
| 1.1 | 2.1 | 1.3 | 1.5 | KP20k.8.test.jsonl.stem.json | X
| 1.0 | 2.0 | 1.3 | 1.4 | KP20k.9.test.jsonl.stem.json |

#### Present
```bash
for i in $(seq 5 6)
do
	python3 util/eval_present.py -i experiments/copy_pres-b9d6765/predictions/KP20k.$i.test.jsonl.stem.json -r ~/ake-datasets/datasets/KP20k/references/test.author.stem.json -n 5 --present ../data/datasets/KP20k.test.jsonl
done
```
| 26.9 | 46.2 | 31.3 | 41.3 | KP20k.0.test.jsonl.stem.json |
| 27.8 | 48.1 | 32.5 | 43.0 | KP20k.1.test.jsonl.stem.json |
| 28.0 | 48.4 | 32.7 | 43.4 | KP20k.2.test.jsonl.stem.json |
| 28.1 | 48.9 | 33.0 | 43.7 | KP20k.3.test.jsonl.stem.json |
| 28.1 | 48.7 | 32.9 | 43.6 | KP20k.4.test.jsonl.stem.json |
| 28.0 | 48.5 | 32.7 | 43.4 | KP20k.5.test.jsonl.stem.json | X Valid
| 28.2 | 49.0 | 33.1 | 43.6 | KP20k.6.test.jsonl.stem.json |
| 28.2 | 49.2 | 33.2 | 43.6 | KP20k.7.test.jsonl.stem.json | X
| 28.1 | 49.0 | 33.0 | 43.6 | KP20k.8.test.jsonl.stem.json |
| 27.6 | 47.4 | 32.1 | 42.5 | KP20k.9.test.jsonl.stem.json |