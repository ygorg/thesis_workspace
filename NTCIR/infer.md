# Infering ntcir dataset


```bash
model="vanilla-0ca64c6"
model="copy_corrnn-02e0a94"
model="copy_less-012a145"
```

```bash
model="copy_corrnn-02e0a94"
for dataset_name in "ntc2-e1g" "ntc2-e1k"
do
	./predict.py -c 0 "experiments/${model}" \
		<(cat ../data/datasets/${dataset_name}.test.jsonl | awk '{ print length, $0 }' | sort -n -s -r | cut -d" " -f2-) \
		--override "{\'model.beam_size\':200,\'model.max_decoding_steps\':6}" \
		--output-file "/home/gallina/ir-using-kg/data/keyphrases/beam200/${dataset_name}.gz.${model}.beam200"
done
```

```bash
model="copy_corrnn-02e0a94"
dataset_name="ntc1-e1"
./predict.py -c 1 "experiments/${model}" \
	<(cat ../data/datasets/${dataset_name}.test.jsonl | awk '{ print length, $0 }' | sort -n -s -r | cut -d" " -f2-) \
	--override "{\'model.beam_size\':200,\'model.max_decoding_steps\':6}" \
	--output-file "/home/gallina/ir-using-kg/data/keyphrases/beam200/${dataset_name}.gz.${model}.beam200"
```