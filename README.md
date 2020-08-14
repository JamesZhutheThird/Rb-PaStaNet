# *Rb-PaSta*Net: A Few-Shot Human-Object Interaction Detection Based on Rules and Part States

### Abstract

Existing Human-Object Interaction (HOI) Detection approaches have achieved great progress on non-rare classes while rare HOI classes are still not well-detected. In this paper, we intend to apply human prior knowledge into the existing work. So we add human-labeled rules to ***PaSta*Net** and propose ***Rb-PaSta*Net** aimed at improving rare HOI classes detection. Our results show a certain improvement of the rare classes, while the non-rare classes and the overall improvement is more considerable. 

### Author
* Shenyu Zhang, Shanghai Jiaotong University
* Zichen Zhu, Shanghai Jiaotong University
* Qingquan Bao, Shanghai Jiaotong University

### Paper
Our paper is available [here](). It will be presented on IMVIP 2020.

### Code 
Our source code is available [here]()

### Getting Started

1. Download dataset and pre-trained weights
``` 
chmod +x ./script/Dataset_download.sh 
./script/Dataset_download.sh 
```

2. Install Python dependencies
```
pip install -r requirements.txt
```

3. Train on HICO-DET
```
python tools/Train_pasta_HICO_DET.py --data 0 --init_weight 1 --train_module 1 --num_iteration 2000000 --model MODELNAME
```

4. Test on HICO-DET
```
python tools/Test_pasta_HICO_DET.py --iteration 2000000 --model MODELNAME
```

5. Generate detection
```
cd ./-Results/
python Generate_detection.py --model 2000000_MODELNAME
```

6. Evaluation
```
cd ./-Results/
python Evaluate_HICO_DET.py --file Detection_2000000_MODELNAME.pkl
```

### MODELNAME & Results

**our_best** (Baseline)
```
('Default: ', 0.2192628749969807)
('Default rare: ', 0.20547882727668224)
('Default non-rare: ', 0.22338018795239453)
('Known object: ', 0.23887022605058528)
('Known object, rare: ', 0.22431761439569864)
('Known object, non-rare: ', 0.2432171100513955)
```

**BOOL**
```
('Default: ', 0.22119324496184756)
('Default rare: ', 0.20543313796226934)
('Default non-rare: ', 0.22590080939029294)
('Known object: ', 0.2403750040644585)
('Known object, rare: ', 0.2242679416250538)
('Known object, non-rare: ', 0.24518620453337156)
```

**EXPDECIMAL**
```
('Default: ', 0.219379421568642)
('Default rare: ', 0.2057141813529523)
('Default non-rare: ', 0.22346124656813374)
('Known object: ', 0.23863934509345058)
('Known object, rare: ', 0.224585892813483)
('Known object, non-rare: ', 0.24283712954071357)
```

### Citation

If you find this work useful, please consider citing:
```
@inproceedings{rbpastanet,
  title={Rb-PaStaNet: A Few-Shot Human-Object Interaction Detection Based on Rules and Part States},
  author={Shenyu Zhang, Zichen Zhu, Qingquan Bao},
  booktitle={IMVIP},
  year={2020}
}
```

### Acknowledgment

Some of the codes are built upon [TIN](https://github.com/DirtyHarryLYL/Transferable-Interactiveness-Network) and [PaStaNet](https://github.com/DirtyHarryLYL/HAKE-Action/tree/Instance-level-HAKE-Action).

We would like to express our very great appreciation to [Cewu Lu](http://mvig.sjtu.edu.cn/) and [Yong-Lu Li](https://dirtyharrylyl.github.io/) for their constructive suggestions and guidance throughout this research work. We would also like to extend our thanks to [Liang Xu](https://liangxuy.github.io/) for his assistance in terms of codes. Their patience and carefulness have been very much appreciated.