# Infering ntcir dataset

model="copy_less-012a145"
for dataset_name in "ntc2-e1g" "ntc2-e1k"
do
	./predict.py -c 0 "experiments/${model}" \
		<(cat ../data/datasets/${dataset_name}.test.jsonl | awk '{ print length, $0 }' | sort -n -s -r | cut -d" " -f2-) \
		--override "{'model.beam_size':200}" \
		--output-file "/home/gallina/ir-using-kg/data/keyphrases/beam200/${dataset_name}.gz.${model}.beam200"
done

model="copy_less-012a145"
dataset_name="ntc1-e1"
./predict.py -c 1 "experiments/${model}" \
	<(cat ../data/datasets/${dataset_name}.test.jsonl | awk '{ print length, $0 }' | sort -n -s -r | cut -d" " -f2-) \
	--override "{'model.beam_size':200}" \
	--output-file "/home/gallina/ir-using-kg/data/keyphrases/beam200/${dataset_name}.gz.${model}.beam200"


dataset_name="ntc2-e1k"
model="seq2seq-allen/experiments/vanilla-0ca64c6"
model="mac/experiments/copy_corrnn-02e0a94"

dataset_name="ntc1-e1"
dataset_name="ntc2-e1g"
dataset_name="ntc2-e1k"



./predict.py -c 0 "${model}" \
	<(cat ../data/datasets/${dataset_name}.test.jsonl | awk '{ print length, $0 }' | sort -n -s -r | cut -d" " -f2-) \
	--override "{model.beam_size:200}" \
	--output-file "/home/gallina/ir-using-kg/data/keyphrases/toprocess/beam200/${dataset_name}.gz.${model}.beam200"