import pandas as pd
from sentence_transformers import SentenceTransformer, util
import argparse, os

def validate_file(f):
    if not os.path.exists(f):
        # Argparse uses the ArgumentTypeError to give a rejection message like:
        # error: argument input: x does not exist
        raise argparse.ArgumentTypeError("{0} does not exist".format(f))
    return f

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
    
    # path of input file to be modified
    input_file_path = './data/in.csv'
    # selected column of input file to be modified
    input_col = 3
    # path of ground truth file for reference
    ground_truth_file_path = './data/gt.csv'
    # selected column of ground truth file for reference
    ground_truth_col = 1
    # top k result(s) to be saved
    top_k = 3

    validate_file(input_file_path)
    validate_file(ground_truth_file_path)
    print('input file to be modified: ', input_file_path)
    print('selected column of input file to be modified: ', input_col)
    print('ground truth file for reference: ', ground_truth_file_path)
    print('selected column of ground truth file for reference: ', ground_truth_col)
    print('top k result(s) to be saved for each input name: ', top_k)

    input, gt = get_data(input_file_path, ground_truth_file_path, input_col, ground_truth_col)
    
    model = SentenceTransformer('all-MiniLM-L6-v2')
    hits = pair_compute(input, gt, model, top_k)
    output = get_output(hits, input, gt, top_k)
    save_prediction(input_file_path, output)
    
