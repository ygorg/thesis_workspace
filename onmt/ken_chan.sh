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
	-pred_path pred/kp20k.ml.one2many.cat.copy.coverage.review.bi-directional.20200930-112944 -remove_title_eos -replace_unk -max_eos_per_output_seq 1 -max_length 60 -batch_size 20 -n_best 1 -beam_size 1

# catSeqTG
python3 train.py -data data/kp20k_tg_sorted/ -vocab data/kp20k_tg_sorted/ -exp_path exp/%s.%s -exp kp20k
	-train_ml -copy_attention -title_guided -one2many -one2many_mode 1
	-epochs 20 -batch_size 12 -batch_workers 3 -seed 9527

DATASET="KDD"
python3 interactive_predict.py \
	-src_file "data/${DATASET}/data_for_corenlp/${DATASET}_testing_context_for_corenlp.txt" -vocab data/kp20k_tg_sorted/ -model model/kp20k.ml.tg.one2many.cat.copy.bi-directional.20200930-112752/kp20k.ml.tg.one2many.cat.copy.bi-directional.epoch=5.batch=14572.total_batch=76000.model \
	-copy_attention -title_guided -one2many -one2many_mode 1 \
	-pred_path pred/kp20k.ml.tg.one2many.cat.copy.bi-directional.20200930-112752 -remove_title_eos -replace_unk -max_eos_per_output_seq 1 -max_length 60 -batch_size 15 -n_best 1 -beam_size 1

# TGNet
python3 train.py -data data/kp20k_tg_sorted/ -vocab data/kp20k_tg_sorted/ -exp_path exp/%s.%s -exp kp20k
	-train_ml -copy_attention -title_guided
	-epochs 20 -batch_size 12 -batch_workers 3 -seed 9527

  kp20k.ml.tg.copy.bi-directional.epoch=2.batch=1348.total_batch=48000.model
  kp20k.ml.tg.copy.bi-directional.epoch=2.batch=5348.total_batch=52000.model
  kp20k.ml.tg.copy.bi-directional.epoch=2.batch=9348.total_batch=56000.model
 kp20k.ml.tg.copy.bi-directional.epoch=2.batch=13348.total_batch=60000.model
 kp20k.ml.tg.copy.bi-directional.epoch=2.batch=21348.total_batch=68000.model
 kp20k.ml.tg.copy.bi-directional.epoch=2.batch=25348.total_batch=72000.model
 kp20k.ml.tg.copy.bi-directional.epoch=2.batch=33348.total_batch=80000.model
 kp20k.ml.tg.copy.bi-directional.epoch=2.batch=37348.total_batch=84000.model
 kp20k.ml.tg.copy.bi-directional.epoch=2.batch=41348.total_batch=88000.model
  kp20k.ml.tg.copy.bi-directional.epoch=3.batch=2696.total_batch=96000.model
kp20k.ml.tg.copy.bi-directional.epoch=3.batch=10696.total_batch=104000.model
kp20k.ml.tg.copy.bi-directional.epoch=3.batch=14696.total_batch=108000.model
kp20k.ml.tg.copy.bi-directional.epoch=3.batch=18696.total_batch=112000.model
kp20k.ml.tg.copy.bi-directional.epoch=3.batch=26696.total_batch=120000.model
kp20k.ml.tg.copy.bi-directional.epoch=3.batch=38696.total_batch=132000.model
kp20k.ml.tg.copy.bi-directional.epoch=3.batch=42696.total_batch=136000.model

python3 interactive_predict.py \
	-src_file "data/${DATASET}/data_for_corenlp/${DATASET}_testing_context_for_corenlp.txt" -vocab data/kp20k_tg_sorted/ -model model/kp20k.ml.tg.copy.bi-directional.20200930-225608/kp20k.ml.tg.copy.bi-directional.epoch=3.batch=42696.total_batch=136000.model \
	-copy_attention -title_guided \
	-pred_path pred/kp20k.ml.tg.copy.bi-directional.20200930-112752 -remove_title_eos -replace_unk -max_eos_per_output_seq 1 -max_length 6 -batch_size 20 -n_best 50 -beam_size 50
