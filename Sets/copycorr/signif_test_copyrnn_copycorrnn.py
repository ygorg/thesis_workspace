
N="5"; method="CopyRNN"; python3 eval.py -n $N -i "output/NTCIR1+2/NTCIR1+2.${method}.stem.json" -r "/home/gallina/ake-datasets/datasets/NTCIR1+2/references/test.indexer.stem.json" --output "output/NTCIR1+2/NTCIR1+2.${method}.top${N}.stem.txt"
N="5"; method="CopyCorrRNN"; python3 eval.py -n $N -i "output/NTCIR1+2/NTCIR1+2.${method}.stem.json" -r "/home/gallina/ake-datasets/datasets/NTCIR1+2/references/test.indexer.stem.json" --output "output/NTCIR1+2/NTCIR1+2.${method}.top${N}.stem.txt"


method1="CopyRNN.top5"
method2="CopyCorrRNN.top5"
file="NTCIR1+2"; file="ntc2"; file="ntc1-e1"; file="ntc2-e1g"; file="ntc2-e1k"
echo "$file"
for i in $(seq 1 4)
do
	python3 stats.py --input1 "output/NTCIR1+2/${file}.${method1}.stem.txt" --input2 "output/NTCIR1+2/${file}.${method2}.stem.txt" --col $i
done

# Split NTCIR candidate into 3 files
# Create a NTCIR2 candidate file
# method="CopyRNN.top5"; cat "output/NTCIR1+2/ntc2-e1g.${method}.stem.txt" "output/NTCIR1+2/ntc2-e1k.${method}.stem.txt" > "output/NTCIR1+2/ntc2.${method}.stem.txt"

method = 'CopyRNN.top5'

with open('../ake-datasets/datasets/NTCIR1+2/src/ntc1-e1.ids') as f: 
	ntc1e1 = set(l for l in f)

with open('../ake-datasets/datasets/NTCIR1+2/src/ntc2-e1g.ids') as f: 
	ntc2e1g = set(l for l in f)


with open('../ake-datasets/datasets/NTCIR1+2/src/ntc2-e1k.ids') as f: 
	ntc2e1k = set(l for l in f)

fntc1e1 = open('output/NTCIR1+2/ntc1-e1.{}.stem.txt'.format(method), 'w')
fntc2e1g = open('output/NTCIR1+2/ntc2-e1g.{}.stem.txt'.format(method), 'w')
fntc2e1k = open('output/NTCIR1+2/ntc2-e1k.{}.stem.txt'.format(method), 'w')

with open('output/NTCIR1+2/NTCIR1+2.{}.stem.txt'.format(method)) as f:
	for l in f:
		ii = l.split('\t')[0] + '\n'
		if ii in ntc1e1:
			fntc1e1.write(l)
		elif ii in ntc2e1g:
			fntc2e1g.write(l)
		elif ii in ntc2e1k:
			fntc2e1k.write(l)
		else:
			print(ii)
			input()


TOP5
```
ntc*
P   stat=-64.677, pva=0.0
R   stat=81.634,  pva=0.0
F   stat=22.834,  pva=2.6031865761892697e-115
MAP stat=117.478, pva=0.0

ntc2-e1g + ntc2-e1k
P   stat=21.561, pva=6.236408115197865e-103
R   stat=12.716, pva=5.072863045969561e-37
F   stat=17.826, pva=5.405009915381679e-71
MAP stat=24.565, pva=5.9122943299549044e-133

ntc2-e1g
P   stat=5.956, pva=2.59422948532717e-09
R   stat=0.922, pva=0.35631200607736957
F   stat=3.874, pva=0.0001073306493501273
MAP stat=6.417, pva=1.3989752673889856e-10

ntc2-e1k
P   stat=25.878, pva=8.164576351441124e-147
R   stat=21.183, pva=3.297038416918879e-99
F   stat=24.327, pva=4.597105271622194e-130
MAP stat=34.173, pva=2.153672504021087e-253

ntc1-e1
P   stat=-88.130, pva=0.0
R   stat=92.732, pva=0.0
F   stat=15.378, pva=2.4676214598178443e-53
MAP stat=127.683, pva=0.0
```