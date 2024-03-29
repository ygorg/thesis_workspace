onmt_translate --model experiments/copyRNN_RefSeerX/model_step_108894.pt \
			   --src <(tail -n 150000 data/NTCIR1+2/NTCIR1+2.src) \
			   --output experiments/copyRNN_RefSeerX/predictions/NTCIR1+2.test.50.108894.txt.150000 \
			   --dynamic_dict --beam_size 50 --max_length 6 --n_best 50 --batch_size 16 --gpu 1