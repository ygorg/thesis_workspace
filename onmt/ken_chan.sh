python3 train.py
	-data data/kp20k_sorted/
	-vocab data/kp20k_sorted/
	-train_ml
	-copy_attention
	-one2many
	-one2many_mode 1

	-exp_path exp/%s.%s
	-exp kp20k
	-epochs 20
	-batch_size 12
	-seed 9527

python3 integrated_data_preprocess.py -json_home ../data/datasets/SemEval-2010-abstract.test.jsonl -dataset SemEval-2010-abstract -data_type testing -saved_home data/SemEval-2010 -dups_info_home data/SemEval-2010/dups_info

python3 integrated_data_preprocess.py -json_home ../data/datasets/NTCIR1+2.test.jsonl -dataset NTCIR1+2 -data_type testing -saved_home data/NTCIR1+2 -dups_info_home data/NTCIR1+2/dups_info

DATASET=KP20k

# catSeqCorr
python3 train.py -data data/kp20k_sorted/ -vocab data/kp20k_sorted/ -exp_path exp/%s.%s -exp kp20k
	-train_ml -copy_attention -coverage_attn -review_attn -one2many -one2many_mode 1
	-epochs 20 -batch_size 12 -seed 9527
python3 interactive_predict.py \
	-src_file "data/${DATASET}/data_for_corenlp/${DATASET}_testing_context_for_corenlp.txt" -vocab data/kp20k_sorted/ -model model/kp20k.ml.one2many.cat.copy.coverage.review.bi-directional.20200930-112944/kp20k.ml.one2many.cat.copy.coverage.review.bi-directional.epoch=4.batch=9929.total_batch=56000.model \
	-copy_attention -coverage_attn -review_attn -one2many -one2many_mode 1 \
	-pred_path pred/%s.%s -remove_title_eos -replace_unk -max_eos_per_output_seq 1 -max_length 60 -batch_size 20 -n_best 1 -beam_size 1

# catSeqTG
python3 train.py -data data/kp20k_tg_sorted/ -vocab data/kp20k_tg_sorted/ -exp_path exp/%s.%s -exp kp20k
	-train_ml -copy_attention -title_guided -one2many -one2many_mode 1
	-epochs 20 -batch_size 12 -batch_workers 3 -seed 9527
python3 interactive_predict.py \
	-src_file "data/${DATASET}/data_for_corenlp/${DATASET}_testing_context_for_corenlp.txt" -vocab data/kp20k_tg_sorted/ -model model/kp20k.ml.tg.one2many.cat.copy.bi-directional.20200930-112752/kp20k.ml.tg.one2many.cat.copy.bi-directional.epoch=5.batch=14572.total_batch=76000.model \
	-copy_attention -title_guided -one2many -one2many_mode 1 \
	-pred_path pred/%s.%s -remove_title_eos -replace_unk -max_eos_per_output_seq 1 -max_length 60 -batch_size 20 -n_best 1 -beam_size 1

# TGNet
python3 train.py -data data/kp20k_tg_sorted/ -vocab data/kp20k_tg_sorted/ -exp_path exp/%s.%s -exp kp20k
	-train_ml -copy_attention -title_guided
	-epochs 20 -batch_size 12 -batch_workers 3 -seed 9527
python3 interactive_predict.py
	-src_file "data/${DATASET}/data_for_corenlp/${DATASET}_testing_context_for_corenlp.txt" -vocab data/kp20k_tg_sorted/ -model model/kp20k.ml.tg.copy.bi-directional.20200930-112752/kp20k.ml.tg.copy.bi-directional.epoch=XXX.batch=XXX.total_batch=XXX.model
	-copy_attention -title_guided
	-pred_path pred/%s.%s -remove_title_eos -replace_unk -max_eos_per_output_seq 1 -max_length 6 -batch_size 20 -n_best 50 -beam_size 50
