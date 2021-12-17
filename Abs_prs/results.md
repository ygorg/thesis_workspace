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
| CopySci   | 27.6 | 33.0 |  4.8 |
| CopySci_p | 27.4 | 32.7 |  1.2 |
| CopySci_a |  8.5 | 21.7 |  4.9 |

Nb de PRMU générés par les modèles
| Model     | P    | R    | M    | U    |
|:--------- | ----:| ----:| ----:| ----:|
| CopySci   | 60.8 | 13.8 | 11.1 | 14.1 |
| CopySci_p | 83.7 |  5.9 |  2.5 |  7.9 |
| CopySci_a | 11.6 | 29.9 | 30.0 | 28.6 |

Nb de PRMU @5 générés par les modèles
| Model@5   | P    | R    | M    | U    |
|:--------- | ----:| ----:| ----:| ----:|
| CopySci   | 92.0 |  3.0 |  2.9 |  2.2 |
| CopySci_p | 99.4 |  0.2 |  0.2 |  0.2 |
| CopySci_a | 16.7 | 28.6 | 28.1 | 26.7 |



| Model/F@5  | All  | Pres | Abs  |
|:---------- | ----:| ----:| ----:|
| CopyNews   | 46.3 | 40.7 | 30.1 |
| CopyNews_p | 33.0 | 40.7 |  0.8 |
| CopyNews_a | 28.2 |  4.4 | 30.6 |




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

* Two step approach : but de généraliser le set de TC.


## KPTimes
The scores seem to always be lower than the original model
The original assumption was that given a "better" reference, thus KPTimes beign better than KP20k the pres and absent models would be better than the original. This is not the case.
The generation is therefore limited by the model !

Pres model : best valid epoch : 2
Abs model : best valid epoch : 0

# Annex

## All metrics for every model

### All CopySci
| P@5  | R@5  | F@5  | MAP  | Model |
| 28.2 | 29.6 | 27.6 | 28.5 | All     KP20k.test.stem.json |
| 28.2 | 48.9 | 33.0 | 43.5 | Present KP20k.test.stem.json |
|  3.7 |  8.5 |  4.8 |  6.0 | Absent  KP20k.test.stem.json |

### Absent CopySci_a La tâche consiste a prédire des séquences qui n'apparaissent pas dans l'entrée en générant un mot ou en copiant un mot de l'entrée.
| P@5  | R@5  | F@5  | MAP  | Model |
|  8.5 |  9.3 |  8.5 |  7.7 | All     KP20k.7.test.stem.json |
| 20.5 | 29.0 | 21.7 | 20.3 | Present KP20k.7.test.stem.json |
|  3.7 |  8.6 |  4.9 |  6.3 | Absent  KP20k.7.test.stem.json | 

### Present CopySci_p
| P@5  | R@5  | F@5  | MAP  | Model |
| 28.1 | 29.3 | 27.4 | 27.8 | All     KP20k.test.stem.json |
| 28.0 | 48.5 | 32.7 | 43.4 | Present KP20k.test.stem.json |
|  1.0 |  1.9 |  1.2 |  1.4 | Absent  KP20k.test.stem.json |


### All CopyNews
| P@5  | R@5  | F@5  | MAP  | TopN | Model |
| 46.5 | 49.5 | 46.3 | 50.9 |    5 | All	NYTime.test.stem |
| 24.6 | 46.3 | 30.1 | 40.7 |    5 | Present	NYTime.test.stem |
| 33.1 | 64.3 | 40.7 | 58.9 |    5 | Absent	NYTime.test.stem |

### Absent CopyNews_a
| P@5  | R@5  | F@5  | MAP  | TopN | Model |
| 18.6 | 20.3 | 18.7 | 18.1 |    5 | All		NYTime.Copy_News_Abs.0.stem.json | X Valid
|  2.3 |  4.9 |  2.9 |  3.5 |    5 | Present	NYTime.Copy_News_Abs.0.stem.json | X Valid
| 16.4 | 31.4 | 20.2 | 26.6 |    5 | Absent	NYTime.Copy_News_Abs.0.stem.json | X Valid

| 28.4 | 30.2 | 28.2 | 28.2 |    5 | All		NYTime.Copy_News_Abs.7.stem.json | X
|  3.6 |  7.1 |  4.4 |  4.7 |    5 | Present	NYTime.Copy_News_Abs.6.stem.json | X
| 24.8 | 47.7 | 30.6 | 41.7 |    5 | Absent	NYTime.Copy_News_Abs.7.stem.json | X

### Present CopyNews_p
| P@5  | R@5  | F@5  | MAP  | TopN | Model |
| 32.5 | 33.3 | 31.8 | 32.4 |    5 | All		NYTime.Copy_News_Prs.2.stem.json | X Valid
| 32.0 | 62.1 | 39.4 | 57.6 |    5 | Present	NYTime.Copy_News_Prs.2.stem.json | X Valid
|  0.5 |  1.0 |  0.6 |  0.8 |    5 | Absent		NYTime.Copy_News_Prs.2.stem.json | X Valid

| 33.7 | 34.6 | 33.0 | 33.8 |    5 | All		NYTime.Copy_News_Prs.7.stem.json | X
| 33.1 | 64.2 | 40.7 | 59.7 |    5 | Present	NYTime.Copy_News_Prs.7.stem.json | X
|  0.7 |  1.3 |  0.8 |  1.1 |    5 | Absent		NYTime.Copy_News_Prs.7.stem.json | X


## Evaluating Present and Absent models for **each epoch**

### Absent CopySci_a
#### Reference All
| 8.7 | 9.7 | 8.9 | 7.9 |  5 | KP20k.0.test.jsonl.stem.json |
| 8.5 | 9.4 | 8.6 | 7.7 |  5 | KP20k.1.test.jsonl.stem.json |
| 8.1 | 8.9 | 8.2 | 7.4 |  5 | KP20k.2.test.jsonl.stem.json |
| 8.6 | 9.4 | 8.7 | 7.7 |  5 | KP20k.3.test.jsonl.stem.json |
| 8.1 | 8.9 | 8.2 | 7.3 |  5 | KP20k.4.test.jsonl.stem.json |
| 8.9 | 9.7 | 8.9 | 8.0 |  5 | KP20k.5.test.jsonl.stem.json | X
| 8.7 | 9.6 | 8.8 | 7.9 |  5 | KP20k.6.test.jsonl.stem.json |
| 8.5 | 9.3 | 8.5 | 7.7 |  5 | KP20k.7.test.jsonl.stem.json | Valid X
| 8.7 | 9.5 | 8.8 | 7.8 |  5 | KP20k.8.test.jsonl.stem.json |
| 8.4 | 9.2 | 8.4 | 7.5 |  5 | KP20k.9.test.jsonl.stem.json |
| 8.4 | 9.2 | 8.4 | 7.5 |  5 | KP20k.10.test.jsonl.stem.json |
| 8.3 | 9.1 | 8.3 | 7.4 |  5 | KP20k.11.test.jsonl.stem.json |
| 8.0 | 8.8 | 8.1 | 7.1 |  5 | KP20k.12.test.jsonl.stem.json |
| 7.8 | 8.6 | 7.9 | 6.9 |  5 | KP20k.13.test.jsonl.stem.json |
| 7.7 | 8.4 | 7.7 | 6.8 |  5 | KP20k.14.test.jsonl.stem.json |
#### Reference Absent
| 2.2 | 5.0 | 2.9 | 3.6 |  5 | KP20k.0.test.jsonl.stem.json |
| 2.7 | 6.3 | 3.6 | 4.6 |  5 | KP20k.1.test.jsonl.stem.json |
| 3.2 | 7.3 | 4.2 | 5.4 |  5 | KP20k.2.test.jsonl.stem.json |
| 3.5 | 8.0 | 4.5 | 5.8 |  5 | KP20k.3.test.jsonl.stem.json |
| 3.5 | 8.1 | 4.6 | 5.9 |  5 | KP20k.4.test.jsonl.stem.json |
| 3.6 | 8.4 | 4.7 | 6.3 |  5 | KP20k.5.test.jsonl.stem.json |
| 3.7 | 8.4 | 4.8 | 6.3 |  5 | KP20k.6.test.jsonl.stem.json |
| 3.7 | 8.6 | 4.9 | 6.3 |  5 | KP20k.7.test.jsonl.stem.json | Valid X
| 3.8 | 8.7 | 5.0 | 6.4 |  5 | KP20k.8.test.jsonl.stem.json | X
| 3.7 | 8.4 | 4.8 | 6.3 |  5 | KP20k.9.test.jsonl.stem.json |
| 3.7 | 8.6 | 4.9 | 6.3 |  5 | KP20k.10.test.jsonl.stem.json |
| 3.7 | 8.7 | 4.9 | 6.3 |  5 | KP20k.11.test.jsonl.stem.json |
| 3.6 | 8.4 | 4.8 | 6.3 |  5 | KP20k.12.test.jsonl.stem.json |
| 3.6 | 8.5 | 4.8 | 6.3 |  5 | KP20k.13.test.jsonl.stem.json |
| 3.5 | 8.2 | 4.7 | 6.1 |  5 | KP20k.14.test.jsonl.stem.json |
#### Reference Present
| 20.4 | 33.0 | 23.2 | 23.2 |  5 | KP20k.0.test.jsonl.stem.json | X
| 20.3 | 31.9 | 22.7 | 22.3 |  5 | KP20k.1.test.jsonl.stem.json |
| 21.2 | 30.9 | 22.8 | 21.5 |  5 | KP20k.2.test.jsonl.stem.json |
| 20.7 | 30.1 | 22.3 | 21.1 |  5 | KP20k.3.test.jsonl.stem.json |
| 21.3 | 29.3 | 22.2 | 20.6 |  5 | KP20k.4.test.jsonl.stem.json |
| 20.9 | 30.0 | 22.3 | 21.0 |  5 | KP20k.5.test.jsonl.stem.json |
| 21.1 | 29.4 | 22.1 | 20.7 |  5 | KP20k.6.test.jsonl.stem.json |
| 20.5 | 29.0 | 21.7 | 20.3 |  5 | KP20k.7.test.jsonl.stem.json | Valid X
| 21.1 | 29.1 | 22.1 | 20.6 |  5 | KP20k.8.test.jsonl.stem.json |
| 20.8 | 27.7 | 21.4 | 19.4 |  5 | KP20k.9.test.jsonl.stem.json |
| 20.8 | 27.7 | 21.3 | 19.3 |  5 | KP20k.10.test.jsonl.stem.json |
| 20.8 | 27.9 | 21.5 | 19.4 |  5 | KP20k.11.test.jsonl.stem.json |
| 20.4 | 26.0 | 20.4 | 18.3 |  5 | KP20k.12.test.jsonl.stem.json |
| 20.4 | 25.1 | 20.1 | 17.8 |  5 | KP20k.13.test.jsonl.stem.json |
| 20.2 | 24.7 | 19.8 | 17.4 |  5 | KP20k.14.test.jsonl.stem.json |

### Present CopySci_p
#### Reference All
| 26.9 | 28.0 | 26.2 | 26.5 |  5 | KP20k.0.test.jsonl.stem.json |
| 27.8 | 29.1 | 27.2 | 27.5 |  5 | KP20k.1.test.jsonl.stem.json |
| 28.0 | 29.3 | 27.4 | 27.8 |  5 | KP20k.2.test.jsonl.stem.json |
| 28.1 | 29.6 | 27.6 | 27.9 |  5 | KP20k.3.test.jsonl.stem.json |
| 28.2 | 29.5 | 27.6 | 28.0 |  5 | KP20k.4.test.jsonl.stem.json |
| 28.1 | 29.3 | 27.4 | 27.8 |  5 | KP20k.5.test.jsonl.stem.json | X Valid
| 28.2 | 29.6 | 27.7 | 27.9 |  5 | KP20k.6.test.jsonl.stem.json |
| 28.2 | 29.7 | 27.7 | 27.9 |  5 | KP20k.7.test.jsonl.stem.json | X
| 28.1 | 29.6 | 27.6 | 27.9 |  5 | KP20k.8.test.jsonl.stem.json |
| 27.6 | 28.6 | 26.8 | 27.2 |  5 | KP20k.9.test.jsonl.stem.json |
#### Reference Absent
|  0.7 |  1.3 |  0.8 |  1.0 |  5 | KP20k.0.test.jsonl.stem.json |
|  0.9 |  1.7 |  1.0 |  1.2 |  5 | KP20k.1.test.jsonl.stem.json |
|  1.0 |  1.8 |  1.1 |  1.3 |  5 | KP20k.2.test.jsonl.stem.json |
|  1.0 |  1.9 |  1.2 |  1.4 |  5 | KP20k.3.test.jsonl.stem.json |
|  1.1 |  2.0 |  1.3 |  1.4 |  5 | KP20k.4.test.jsonl.stem.json |
|  1.0 |  1.9 |  1.2 |  1.4 |  5 | KP20k.5.test.jsonl.stem.json | X Valid
|  1.1 |  2.0 |  1.3 |  1.5 |  5 | KP20k.6.test.jsonl.stem.json |
|  1.1 |  2.0 |  1.3 |  1.4 |  5 | KP20k.7.test.jsonl.stem.json |
|  1.1 |  2.1 |  1.3 |  1.5 |  5 | KP20k.8.test.jsonl.stem.json | X
|  1.0 |  2.0 |  1.3 |  1.4 |  5 | KP20k.9.test.jsonl.stem.json |
#### Reference Present
| 26.9 | 46.2 | 31.3 | 41.3 |  5 | KP20k.0.test.jsonl.stem.json |
| 27.8 | 48.1 | 32.5 | 43.0 |  5 | KP20k.1.test.jsonl.stem.json |
| 28.0 | 48.4 | 32.7 | 43.4 |  5 | KP20k.2.test.jsonl.stem.json |
| 28.1 | 48.9 | 33.0 | 43.7 |  5 | KP20k.3.test.jsonl.stem.json |
| 28.1 | 48.7 | 32.9 | 43.6 |  5 | KP20k.4.test.jsonl.stem.json |
| 28.0 | 48.5 | 32.7 | 43.4 |  5 | KP20k.5.test.jsonl.stem.json | X Valid
| 28.2 | 49.0 | 33.1 | 43.6 |  5 | KP20k.6.test.jsonl.stem.json |
| 28.2 | 49.2 | 33.2 | 43.6 |  5 | KP20k.7.test.jsonl.stem.json | X
| 28.1 | 49.0 | 33.0 | 43.6 |  5 | KP20k.8.test.jsonl.stem.json |
| 27.6 | 47.4 | 32.1 | 42.5 |  5 | KP20k.9.test.jsonl.stem.json |



### Absent CopyNews_a
#### Reference All
| 18.63 | 20.28 | 18.71 | 18.12 |  5 | NYTime.Copy_News_Abs.0.stem.json | X Valid
| 23.85 | 25.74 | 23.86 | 23.91 |  5 | NYTime.Copy_News_Abs.1.stem.json |
| 26.33 | 28.18 | 26.24 | 26.03 |  5 | NYTime.Copy_News_Abs.2.stem.json |
| 27.38 | 29.26 | 27.27 | 27.33 |  5 | NYTime.Copy_News_Abs.3.stem.json |
| 27.75 | 29.56 | 27.60 | 27.60 |  5 | NYTime.Copy_News_Abs.4.stem.json |
| 27.84 | 29.56 | 27.64 | 27.73 |  5 | NYTime.Copy_News_Abs.5.stem.json |
| 28.18 | 29.97 | 28.00 | 28.06 |  5 | NYTime.Copy_News_Abs.6.stem.json |
| 28.36 | 30.16 | 28.18 | 28.23 |  5 | NYTime.Copy_News_Abs.7.stem.json | X
#### Reference Abs
| 16.38 | 31.41 | 20.15 | 26.55 |  5 | NYTime.Copy_News_Abs.0.stem.json | X Valid
| 21.21 | 40.16 | 25.95 | 34.77 |  5 | NYTime.Copy_News_Abs.1.stem.json |
| 23.00 | 44.24 | 28.31 | 38.30 |  5 | NYTime.Copy_News_Abs.2.stem.json |
| 24.05 | 45.73 | 29.48 | 40.17 |  5 | NYTime.Copy_News_Abs.3.stem.json |
| 24.47 | 46.50 | 29.99 | 40.76 |  5 | NYTime.Copy_News_Abs.4.stem.json |
| 24.60 | 46.60 | 30.11 | 40.88 |  5 | NYTime.Copy_News_Abs.5.stem.json |
| 24.63 | 46.67 | 30.16 | 41.05 |  5 | NYTime.Copy_News_Abs.6.stem.json |
| 24.83 | 47.70 | 30.56 | 41.74 |  5 | NYTime.Copy_News_Abs.7.stem.json | X
#### Reference Prs
|  2.26 |  4.87 |  2.85 |  3.49 |  5 | NYTime.Copy_News_Abs.0.stem.json | X Valid
|  2.70 |  5.65 |  3.37 |  3.97 |  5 | NYTime.Copy_News_Abs.1.stem.json |
|  3.40 |  6.77 |  4.19 |  4.51 |  5 | NYTime.Copy_News_Abs.2.stem.json |
|  3.42 |  6.85 |  4.21 |  4.42 |  5 | NYTime.Copy_News_Abs.3.stem.json |
|  3.38 |  6.70 |  4.15 |  4.33 |  5 | NYTime.Copy_News_Abs.4.stem.json |
|  3.33 |  6.46 |  4.06 |  4.32 |  5 | NYTime.Copy_News_Abs.5.stem.json |
|  3.64 |  7.10 |  4.44 |  4.65 |  5 | NYTime.Copy_News_Abs.6.stem.json | X
|  3.65 |  6.85 |  4.41 |  4.63 |  5 | NYTime.Copy_News_Abs.7.stem.json |

### Present CopyNews_p
#### Reference All
| 29.47 | 30.25 | 28.83 | 28.84 |  5 | NYTime.Copy_News_Prs.0.stem.json |
| 31.45 | 32.20 | 30.74 | 31.15 |  5 | NYTime.Copy_News_Prs.1.stem.json |
| 32.47 | 33.32 | 31.77 | 32.39 |  5 | NYTime.Copy_News_Prs.2.stem.json | X Valid
| 32.89 | 33.71 | 32.15 | 32.95 |  5 | NYTime.Copy_News_Prs.3.stem.json |
| 33.23 | 34.10 | 32.50 | 33.26 |  5 | NYTime.Copy_News_Prs.4.stem.json |
| 33.12 | 33.94 | 32.38 | 33.26 |  5 | NYTime.Copy_News_Prs.5.stem.json |
| 33.17 | 34.01 | 32.44 | 33.26 |  5 | NYTime.Copy_News_Prs.6.stem.json |
| 33.69 | 34.55 | 32.95 | 33.78 |  5 | NYTime.Copy_News_Prs.7.stem.json | X
| 33.34 | 34.17 | 32.59 | 33.42 |  5 | NYTime.Copy_News_Prs.8.stem.json |
| 33.40 | 34.27 | 32.68 | 33.36 |  5 | NYTime.Copy_News_Prs.9.stem.json |
#### Reference Abs
|  0.09 |  0.20 |  0.12 |  0.27 |  5 | NYTime.Copy_News_Prs.0.stem.json |
|  0.20 |  0.39 |  0.25 |  0.40 |  5 | NYTime.Copy_News_Prs.1.stem.json |
|  0.50 |  1.04 |  0.63 |  0.81 |  5 | NYTime.Copy_News_Prs.2.stem.json | X Valid
|  0.43 |  0.80 |  0.52 |  0.75 |  5 | NYTime.Copy_News_Prs.3.stem.json |
|  0.50 |  0.99 |  0.62 |  0.87 |  5 | NYTime.Copy_News_Prs.4.stem.json |
|  0.45 |  0.92 |  0.56 |  0.85 |  5 | NYTime.Copy_News_Prs.5.stem.json |
|  0.45 |  0.88 |  0.55 |  0.77 |  5 | NYTime.Copy_News_Prs.6.stem.json |
|  0.65 |  1.33 |  0.81 |  1.06 |  5 | NYTime.Copy_News_Prs.7.stem.json | X
|  0.44 |  0.81 |  0.53 |  0.77 |  5 | NYTime.Copy_News_Prs.8.stem.json |
|  0.64 |  1.29 |  0.80 |  1.04 |  5 | NYTime.Copy_News_Prs.9.stem.json |
#### Reference Prs
| 29.38 | 56.97 | 36.10 | 51.81 |  5 | NYTime.Copy_News_Prs.0.stem.json |
| 31.25 | 60.55 | 38.39 | 55.81 |  5 | NYTime.Copy_News_Prs.1.stem.json |
| 31.99 | 62.14 | 39.35 | 57.58 |  5 | NYTime.Copy_News_Prs.2.stem.json | X Valid
| 32.47 | 63.05 | 39.94 | 58.84 |  5 | NYTime.Copy_News_Prs.3.stem.json |
| 32.73 | 63.70 | 40.28 | 59.25 |  5 | NYTime.Copy_News_Prs.4.stem.json |
| 32.67 | 63.72 | 40.23 | 59.45 |  5 | NYTime.Copy_News_Prs.5.stem.json |
| 32.74 | 63.86 | 40.33 | 59.57 |  5 | NYTime.Copy_News_Prs.6.stem.json |
| 33.07 | 64.21 | 40.69 | 59.68 |  5 | NYTime.Copy_News_Prs.7.stem.json | X
| 32.91 | 63.89 | 40.47 | 59.41 |  5 | NYTime.Copy_News_Prs.8.stem.json |
| 32.78 | 63.69 | 40.34 | 58.96 |  5 | NYTime.Copy_News_Prs.9.stem.json |
