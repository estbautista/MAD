import os
import math
import pickle
import MAD.MAD
import lsmanip
import lsmanip.io as lio
import lsmanip.subset as lsub

#####################################################
# Helper imports
#####################################################
from config import get_config, set_dir

if __name__ == '__main__':

    # Load config
    config = get_config()

    # Params
    # Path related
    data_path = config['paths']['dataset']

    # Model related
    MAD_context_length = int(config['model']['context_length'])

    # Splitting related
    split_window_size = int(config['splitting']['window_size'])
    split_window_shift = int(config['splitting']['window_shift'])
    train_test_ratio = float(config['splitting']['train_test_ratio'])

    val_ratio = float(config['global']['val_ratio'])


    # Load data
    link_stream = lio.from_csv(data_path)

    # Compute initial timestamp based on train/test split
    num_windows = (link_stream.max_time // split_window_shift) + 1
    train_val_windows = int(round(num_windows * train_test_ratio))
    val_windows = int(round(train_val_windows * val_ratio))
    train_windows = train_val_windows - val_windows

    time_init = train_windows * split_window_shift
    time_end = train_val_windows * split_window_shift

    # Keep only used data
    context_time = MAD_context_length * split_window_shift
    interval = [time_init - context_time, time_end]
    link_stream = lsub.time_partition(link_stream, interval)

    # Snapshots from data
    first_used_window = max(0, train_windows - MAD_context_length)
    edgelist = set()
    for u, v, t in link_stream.to_triplets():
        t_new_min = max(
            first_used_window,
            math.floor((t - split_window_size) / split_window_shift) + 1
        )

        t_new_max = min(
            num_windows - 1,
            math.floor(t / split_window_shift)
        )

        for t_new in range(t_new_min, t_new_max + 1):
            edgelist.add((u, v, t_new))

    link_stream = lsmanip.LinkStream.from_triplets(edgelist)

    # Construct phi. 
    """ Construction of phi.
    Irrelevant to track edges that we know never appear and always have 0 probability. 
    This allows to obtain a significant speed-up by reducing the size of phi. 
    
    In an offline scenario it is not serious to exclude such edges:
    they always appear in the right-part of the tree and never have any activity. 

    In a real-time tracking scenario it may be better to include all the edge space in phi 
    to account for edges that we have never seen but may appear for the first time. """
    phi = list({(u,v) for u,v,t in link_stream.to_triplets()})
    
    # Link stream as tsgraphs
    ls_tsg = link_stream.to_tsgraphs()

    # Process the each timestamp
    out_list = []
    for t in range(train_windows, link_stream.max_time + 1):
        if t % 10 == 0:
            print('Processing timestamp ' + str(t) + ' ...')

        # Set query
        if t in ls_tsg:
            Q = {(u,v,t):1 if (u,v) in ls_tsg[t] else 0 for u,v in phi}
        else:
            Q = {(u,v,t):0 for u,v in phi}

        # Compute context 
        H = lsub.time_partition(link_stream, [t - MAD_context_length, t]).to_triplets()
        
        # Score the query
        score = MAD.MAD.scoring(Q, H)

        # Store result
        out_list += [(t, score)]

    # Saving scores
    out_list = sorted(out_list, key=lambda x: x[0])
    anomaly_scores = [score for _, score in out_list]

    print(f'scores sum: {sum(anomaly_scores)}')

    print('MADagg scoring done.')
