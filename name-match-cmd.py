import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer, util
import argparse, os
from argparse import ArgumentParser

def validate_file(f):
    if not os.path.exists(f):
        # Argparse uses the ArgumentTypeError to give a rejection message like:
        # error: argument input: x does not exist
        raise argparse.ArgumentTypeError("{0} does not exist".format(f))
    return f

parser = ArgumentParser(description="Name matching form Command line.")
parser.add_argument("-i", type=validate_file, required=True,
                    help="input file to be modified")

parser.add_argument("-n", type=int, default=0,
                    help='n-th column of input file to be modified (default: 0, which is the first column)')

parser.add_argument("-g", type=validate_file, required=True,
                    help="ground truth name list for validation")

parser.add_argument("-j",type=int, default=0,
                    help='j-th column of ground truth file for validation (default: 0, which is the first column)')

parser.add_argument("-k",type=int, default=1,
                    help='top k result(s) to be saved for each input name (default: 1, where the result with highest similarity will be saved)')

args = parser.parse_args()

def get_data(i, g, n, j):
    input = pd.read_csv(i, usecols=[n], names=['name'], header=None)
    # input = input.drop_duplicates()
    gt = pd.read_csv(g, usecols=[j], names=['name'], header=None)
    gt = gt.drop_duplicates()
    input = input['name'].tolist()
    gt = gt['name'].tolist()
    return input, gt

def get_score(embeddings1, embeddings2):
    cosine_scores = util.cos_sim(embeddings1, embeddings2)  #Compute cosine-similarities
    cosine_scores = cosine_scores.cpu().numpy()[0]
    return 

def pair_compute(input, gt, model, k):
    query_embeddings = model.encode(input, convert_to_tensor=True)  #Compute embedding for both lists
    corpus_embeddings = model.encode(gt, convert_to_tensor=True)
    hits = util.semantic_search(query_embeddings, corpus_embeddings, score_function=util.dot_score, top_k=k)
    return hits

def get_output(hits, input, gt, k):
    top_results = []
    if k!=1:
        input_ls = []
        for idx, top_k_hit in enumerate(hits):
            for hit in top_k_hit:
                top_result = gt[hit['corpus_id']]
                top_results.append(top_result)
                input_ls.append(input[idx])
        dict = {'query name':input_ls, 'predicted': top_results} 
    else:
        for idx, hit in enumerate(hits):
            hit = hit[0]
            top_result = gt[hit['corpus_id']]
            top_results.append(top_result)
        dict = {'query name':input, 'predicted': top_results} 
    output = pd.DataFrame(dict)
    return output

def save_prediction(save_path, output):
    root, fname = os.path.split(save_path)
    new_fname = root + '/' + fname.split('.')[0] + '_predicted.csv'
    output.to_csv(new_fname, index=False, header=False)

if __name__ == "__main__":
    
    print('input file to be modified: ', args.i)
    print('selected column of input file to be modified: ', args.n)
    print('ground truth file for reference: ', args.g)
    print('selected column of ground truth file for reference: ', args.j)
    print('top k result(s) to be saved for each input name: ', args.k)

    input, gt = get_data(args.i, args.g, args.n, args.j)
    
    model = SentenceTransformer('all-MiniLM-L6-v2')
    hits = pair_compute(input, gt, model, args.k)
    output = get_output(hits, input, gt, args.k)
    save_prediction(args.i, output)
    