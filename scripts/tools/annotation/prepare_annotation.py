#!/usr/bin/env python
"""
This script helps prepare the necessary frames to be annotated for training a custom classifier for given data.

Usage:
  prepare_annotation.py --data_path=DATA_PATH
  prepare_annotation.py (-h | --help)

Options:
  --data_path=DATA_PATH     Full path to the data-set folder
"""

import os
import torch
import glob

from docopt import docopt

from realtimenet import feature_extractors
from realtimenet import engine
from realtimenet.finetuning import compute_features
from realtimenet.finetuning import set_internal_padding_false

if __name__ == "__main__":
    args = docopt(__doc__)
    dataset_path = args['--data_path']

    # Load feature extractor
    feature_extractor = feature_extractors.StridedInflatedEfficientNet()

    # Remove internal padding for feature extraction and training
    checkpoint = torch.load('resources/backbone/strided_inflated_efficientnet.ckpt')
    feature_extractor.load_state_dict(checkpoint)
    feature_extractor.eval()

    # Create Inference Engine
    inference_engine = engine.InferenceEngine(feature_extractor, use_gpu=True)

    for split in ['train', 'valid']:
        print("\n" + "-"*10 + f"Preparing videos in the {split}-set" + "-"*10)
        for label in os.listdir(os.path.join(dataset_path, f'videos_{split}')):
            # Get data-set from path, given split and label
            folder = os.path.join(dataset_path, f'videos_{split}', label)

            # Create features and frames folders for the given split and label
            features_folder = dataset_path + f"features_{split}/{label}/"
            frames_folder = dataset_path + f"frames_{split}/{label}/"
            os.makedirs(features_folder, exist_ok=True)
            os.makedirs(frames_folder, exist_ok=True)

            # Loop through all videos for the given class-label
            videos = glob.glob(folder + '/*.mp4')
            for e, video_path in enumerate(videos):
                print(f"\r  Class: \"{label}\"  -->  Processing video {e + 1} / {len(videos)}", end="")
                path_frames = frames_folder + video_path.split("/")[-1].replace(".mp4", "")
                path_features = features_folder + video_path.split("/")[-1].replace(".mp4", ".npy")
                os.makedirs(path_frames, exist_ok=True)

                # WARNING: if set a max batch size, you should not remove padding from model.
                compute_features(video_path, path_features, inference_engine,
                                 minimum_frames=0,  path_frames=path_frames, batch_size=64)
            print()
    print('\nDone!')
