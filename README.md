# Name matching with pre-trained Sentence Transformer
This repo provides similarity searching for sentence/name, it includes two versions of script, name-match.py and name-match-cmd.py  
Both of them create same result, name-match.py is built for using as function and further modifying, while name-match-cmd.py supports command line operation only. The dockerfile also included for building docker image.

## Getting Started
This function tested under Python 3.9  
Use the pip to install dependencies, you may use conda instead
```
pip install -U sentence-transformers
pip install pandas
```

## name-match.py (Not support command line options)
Please modify below parameters before using

```python
# path of input file to be modified
input_file_path = '/path to/in.csv'

# Selected column of input file to be modified, 
# For single column .csv, please use input_col = 0
input_col = 3

# path of ground truth file for reference, it can be the same file to the input file (Single file with both input list and groundtruth list in different column)
ground_truth_file_path = '/path to/gt.csv'

# selected column of ground truth file for reference
# For single column .csv, please use ground_truth_col = 0
ground_truth_col = 1

# top k result(s) to be saved
top_k = 1
```

## name-match-cmd.py (Support command line options)
```
  -h, --help  show this help message and exit
  -i I        (required) input file to be modified
  -n N        n-th column of input file to be modified (default: 0, which is the first column)
  -g G        (required) ground truth name list for validation, it can be the same file to the input file.
  -j J        j-th column of ground truth file for validation (default: 0, which is the first column)
  -k K        top k result(s) to be saved for each input name (default: 1, where the result with highest similarity will be saved)
```
command format:  
```
python name-match-cmd.py -i required_argument 
                        [-n option_argument] 
                         -g required_argument 
                        [-j option_argument] 
                        [-k option_argument]
```
example for multi-columns data with k=3:
```
python name-match-cmd.py -i /home/data/in.csv -n 3 -g /home/data/gt.csv -j 1 -k 3
```
example for single-column data with default parameters:
```
python name-match-cmd.py -i /home/data/in.csv -g /home/data/gt.csv
```

## Expected input format
The script supports multi-columns .csv files, while the index of the column should be indicated, e.g. the names of input and ground truth file are located in second and third column respectively, then n=1 and j=2. This folder also provide examples of input file (in.csv) and reference/ground truth file (gt.csv).  
The function will not ignore the first line of input files, in case some files are not including headers. Please remove the first line of predicted file if there are headers in your .csv files.

## Expected output format
The prediction will be saved in the same location as input file  
When k=1, only the result with highest similarity will be saved  
Below is the example of saved prediction .csv  
The left column is the alias/misspelled name, the right column is the ground truth/desired name
```
power funding III,"power funding, LP"
harrison invest 2,harrison invest LP
Tony co-invest,Tony co-invest LP
major bank fund 2,Canada major bank fund II 
```

When k larger than 1, k results with highest similarity will be saved  
The row order depends on the similarity in descending order (In here k=3)
```
power funding III,"power funding, LP"
power funding III,goverment support funding
power funding III,apple funding
harrison invest 2,harrison invest LP
harrison invest 2,Tony co-invest LP
harrison invest 2,Credit fund in AICA - permberton credit fund 2(B)
Tony co-invest,Tony co-invest LP
Tony co-invest,harrison invest LP
Tony co-invest,Canada major bank fund II
major bank fund 2,Canada major bank fund II
major bank fund 2,Credit fund in AICA - permberton credit fund 2(B)
major bank fund 2,apple funding 
```

## Docker
Git clone this repo and go to the directory
```
git clone https://github.com/issacchan26/SentenceSimilaritySearching.git
cd SentenceSimilaritySearching
```
Build the image, you may ignore the warning during installing dependencies.
```
docker build -t name-match .
```
Run the image, the below code will mount your local data folder to /app/data inside the image. The predicted file will be created in your local data folder. Please note that the path of input files should start with /app/data/ e.g. the files are stored locally in /home/data/input.csv and /home/data/gt.csv then the options should be /app/data/input.csv and /app/data/gt.csv respectively, i.e.
```
docker run -v /home/data:/app/data -t name-match -i /app/data/input.csv -n 3 -g /app/data/gt.csv -j 4 -k 1
```

