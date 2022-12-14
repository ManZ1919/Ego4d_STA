#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved.

import os
import random
import torch
import torch.utils.data
import json
# from iopath.common.file_io import PathManager
from iopath.common.file_io import g_pathmgr
import slowfast.utils.logging as logging

from . import decoder as decoder
from . import utils as utils
from . import video_container as container
from .build import DATASET_REGISTRY

logger = logging.get_logger(__name__)


@DATASET_REGISTRY.register()
class Ego4dhand(torch.utils.data.Dataset):
    """
    Ego4D video loader. Construct the ego4d video loader, then sample
    clips from the videos. For training and validation, a single clip is
    randomly sampled from every video with random cropping, scaling, and
    flipping. For testing, multiple clips are uniformaly sampled from every
    video with uniform cropping. For uniform cropping, we take the left, center,
    and right crop if the width is larger than height, or take top, center, and
    bottom crop if the height is larger than the width.
    """

    def __init__(self, cfg, mode, num_retries=10):
        """
        Construct the Ego4D video loader with a given csv file. The format of
        the csv file is:
        ```
        path_to_video_1 label_1
        path_to_video_2 label_2
        ...
        path_to_video_N label_N
        ```
        Args:
            cfg (CfgNode): configs.
            mode (string): Options includes `train`, `val`, or `test` mode.
                For the train and val mode, the data loader will take data
                from the train or val set, and sample one clip per video.
                For the test mode, the data loader will take data from test set,
                and sample multiple clips per video.
            num_retries (int): number of retries.
        """
        # Only support train, val, and test mode.
        assert mode in [
            "train",
            "val",
            "test",
            "trainval",
        ], "Split '{}' not supported for Ego4D Hand Anticipation".format(mode)
        self.mode = mode
        self.cfg = cfg

        self._video_meta = {}
        self._num_retries = num_retries
        # For training or validation mode, one single clip is sampled from every
        # video. For testing, NUM_ENSEMBLE_VIEWS clips are sampled from every
        # video. For every clip, NUM_SPATIAL_CROPS is cropped spatially from
        # the frames.
        if self.mode in ["train", "val", "trainval"]:
            self._num_clips = 1
        elif self.mode in ["test"]:
            self.mode = "test_unannotated"
            self._num_clips = (
                cfg.TEST.NUM_ENSEMBLE_VIEWS * cfg.TEST.NUM_SPATIAL_CROPS
            )

        logger.info("Constructing Ego4D {}...".format(mode))
        self._construct_loader()

    def _construct_loader(self):
        """
        Construct the video loader.
        """
        path_to_file = os.path.join(
            self.cfg.DATA.PATH_TO_DATA_DIR, "annotations/fho_hands_{}.json".format(self.mode)
        )
        assert g_pathmgr.exists(path_to_file), "{} dir not found".format(
            path_to_file
        )
        self._path_to_ant_videos = []
        self._labels = []
        self._labels_masks = []
        self._spatial_temporal_idx = []
        f = open(path_to_file)
        # data = json.load(f)
        data = dict(list(json.load(f).items())[5:])
        f.close()
        clip_idx=0
        for clip_id, hand_dicts in data.items():
            for hand_annot in hand_dicts:
                clip_id = hand_annot['clip_id']
                for annot in hand_annot['frames']:
                    pre45_frame = annot['pre_45']['frame']
                    clip_name = str(clip_id)+'_'+str(pre45_frame-1)
                    for idx in range(self._num_clips):
                        self._spatial_temporal_idx.append(idx)
                        self._video_meta[clip_idx * self._num_clips + idx] = {}
                        label=[]
                        label_mask=[]
                        self._path_to_ant_videos.append(
                                os.path.join(self.cfg.DATA.PATH_TO_DATA_DIR, 'cropped_videos_ant', clip_name+'.mp4')
                            )
                        #placeholder for the 1x20 hand gt vector (padd zero when GT is not available)
                        # 5 frames have the following order: pre_45, pre_40, pre_15, pre, contact
                        # GT for each frames has the following order: left_x,left_y,right_x,right_y
                        label= [0.0]*20
                        label_mask = [0.0]*20
                        # for frame_type, frame_annot in hand_annot.items():
                        for frame_type, frame_annot in annot.items():
                            # if frame_type in ['start_sec', 'end_sec','height', 'width']:
                            if frame_type in ["action_start_sec", "action_end_sec","action_start_frame","action_end_frame","action_clip_start_sec","action_clip_end_sec","action_clip_start_frame","action_clip_end_frame"]:
                                continue
                            # frame_gt = frame_annot[1]
                            if len(frame_annot)==2:
                                continue
                            frame_gt = frame_annot['boxes']
                            if frame_type == 'pre_45':
                                for single_hand in frame_gt:
                                    if 'left_hand' in single_hand:
                                        label_mask[0]=1.0
                                        label_mask[1]=1.0
                                        label[0]= single_hand['left_hand'][0]
                                        label[1]= single_hand['left_hand'][1]
                                    if 'right_hand' in single_hand:
                                        label_mask[2]=1.0
                                        label_mask[3]=1.0
                                        label[2]= single_hand['right_hand'][0]
                                        label[3]= single_hand['right_hand'][1]   
                            if frame_type == 'pre_30':
                                for single_hand in frame_gt:
                                    if 'left_hand' in single_hand:
                                        label_mask[4]=1.0
                                        label_mask[5]=1.0
                                        label[4]= single_hand['left_hand'][0]
                                        label[5]= single_hand['left_hand'][1]
                                    if 'right_hand' in single_hand:
                                        label_mask[6]=1.0
                                        label_mask[7]=1.0
                                        label[6]= single_hand['right_hand'][0]
                                        label[7]= single_hand['right_hand'][1]   
                            if frame_type == 'pre_15':
                                for single_hand in frame_gt:
                                    if 'left_hand' in single_hand:
                                        label_mask[8]=1.0
                                        label_mask[9]=1.0
                                        label[8]= single_hand['left_hand'][0]
                                        label[9]= single_hand['left_hand'][1]
                                    if 'right_hand' in single_hand:
                                        label_mask[10]=1.0
                                        label_mask[11]=1.0
                                        label[10]= single_hand['right_hand'][0]
                                        label[11]= single_hand['right_hand'][1]   
                            if frame_type == 'pre_frame':
                                for single_hand in frame_gt:
                                    if 'left_hand' in single_hand:
                                        label_mask[12]=1.0
                                        label_mask[13]=1.0
                                        label[12]= single_hand['left_hand'][0]
                                        label[13]= single_hand['left_hand'][1]
                                    if 'right_hand' in single_hand:
                                        label_mask[14]=1.0
                                        label_mask[15]=1.0
                                        label[14]= single_hand['right_hand'][0]
                                        label[15]= single_hand['right_hand'][1]    
                            if frame_type == 'contact_frame':
                                for single_hand in frame_gt:
                                    if 'left_hand' in single_hand:
                                        label_mask[16]=1.0
                                        label_mask[17]=1.0
                                        label[16]= single_hand['left_hand'][0]
                                        label[17]= single_hand['left_hand'][1]
                                    if 'right_hand' in single_hand:
                                        label_mask[18]=1.0
                                        label_mask[19]=1.0
                                        label[18]= single_hand['right_hand'][0]
                                        label[19]= single_hand['right_hand'][1]   
                        self._labels.append(label)
                        self._labels_masks.append(label_mask)
                    clip_idx+=1
        assert (
            len(self._path_to_ant_videos) > 0
        ), "Failed to load Ego4D split {} from {}".format(
            self._split_idx, path_to_file
        )
        logger.info(
            "Constructing Ego4D dataloader (size: {}) from {}".format(
                len(self._path_to_ant_videos), path_to_file
            )
        )

    def __getitem__(self, index):
        """
        Given the video index, return the list of frames, label, and video
        index if the video can be fetched and decoded successfully, otherwise
        repeatly find a random video that can be decoded as a replacement.
        Args:
            index (int): the video index provided by the pytorch sampler.
        Returns:
            frames (tensor): the frames of sampled from the video. The dimension
                is `channel` x `num frames` x `height` x `width`.
            label (int): the label of the current video.
            index (int): if the video provided by pytorch sampler can be
                decoded, then return the index of the video. If not, return the
                index of the video replacement that can be decoded.
        """
        short_cycle_idx = None
        # When short cycle is used, input index is a tupple.
        if isinstance(index, tuple):
            index, short_cycle_idx = index

        if self.mode in ["train", "val", "trainval"]:
            # -1 indicates random sampling.
            temporal_sample_index = -1
            spatial_sample_index = -1
            min_scale = self.cfg.DATA.TRAIN_JITTER_SCALES[0]
            max_scale = self.cfg.DATA.TRAIN_JITTER_SCALES[1]
            crop_size = self.cfg.DATA.TRAIN_CROP_SIZE
            if short_cycle_idx in [0, 1]:
                crop_size = int(
                    round(
                        self.cfg.MULTIGRID.SHORT_CYCLE_FACTORS[short_cycle_idx]
                        * self.cfg.MULTIGRID.DEFAULT_S
                    )
                )
            if self.cfg.MULTIGRID.DEFAULT_S > 0:
                # Decreasing the scale is equivalent to using a larger "span"
                # in a sampling grid.
                min_scale = int(
                    round(
                        float(min_scale)
                        * crop_size
                        / self.cfg.MULTIGRID.DEFAULT_S
                    )
                )
        elif self.mode in ["test_unannotated"]:
            temporal_sample_index = (
                self._spatial_temporal_idx[index]
                // self.cfg.TEST.NUM_SPATIAL_CROPS
            )
            # spatial_sample_index is in [0, 1, 2]. Corresponding to left,
            # center, or right if width is larger than height, and top, middle,
            # or bottom if height is larger than width.
            spatial_sample_index = (
                self._spatial_temporal_idx[index]
                % self.cfg.TEST.NUM_SPATIAL_CROPS
            )
            min_scale, max_scale, crop_size = [self.cfg.DATA.TEST_CROP_SIZE] * 3
            # The testing is deterministic and no jitter should be performed.
            # min_scale, max_scale, and crop_size are expect to be the same.
            assert len({min_scale, max_scale, crop_size}) == 1
        else:
            raise NotImplementedError(
                "Does not support {} mode".format(self.mode)
            )
        sampling_rate = utils.get_random_sampling_rate(
            self.cfg.MULTIGRID.LONG_CYCLE_SAMPLING_RATE,
            self.cfg.DATA.SAMPLING_RATE,
        )
        # Try to decode and sample a clip from a video. If the video can not be
        # decoded, repeatly find a random video replacement that can be decoded.
        for _ in range(self._num_retries):
            video_container = None
            try:
                video_container = container.get_video_container(
                    self._path_to_ant_videos[index],
                    self.cfg.DATA_LOADER.ENABLE_MULTI_THREAD_DECODE,
                    self.cfg.DATA.DECODING_BACKEND,
                )                
            except Exception as e:
                logger.info(
                    "Failed to load video from {} with error {}".format(
                        self._path_to_ant_videos[index], e
                    )
                )

            # Select a random video if the current video was not able to access.
            if video_container is None:
                index = random.randint(0, len(self._path_to_ant_videos) - 1)
                continue

            # Decode video. Meta info is used to perform selective decoding.
            frames = decoder.decode(
                video_container,
                sampling_rate,
                self.cfg.DATA.NUM_FRAMES,
                temporal_sample_index,
                self.cfg.TEST.NUM_ENSEMBLE_VIEWS,
                video_meta=self._video_meta[index],
                target_fps=self.cfg.DATA.TARGET_FPS,
                backend=self.cfg.DATA.DECODING_BACKEND,
                max_spatial_scale=max_scale,
            )

     
            assert (frames is not None),  "Failed to load from {}".format(self._path_to_ant_videos[index] )

            # If decoding failed (wrong format, video is too short, and etc),
            # select another video.
            # if initial_frames is None:
            #     index = random.randint(0, len(self._path_to_videos) - 1)
            #     continue

            # Perform color normalization.
            frames = utils.tensor_normalize(
                frames, self.cfg.DATA.MEAN, self.cfg.DATA.STD
            )
            # T H W C -> C T H W.
            frames = frames.permute(3, 0, 1, 2)

            frames = utils.spatial_sampling(
                frames,
                spatial_idx=spatial_sample_index,
                min_scale=min_scale,
                max_scale=max_scale,
                crop_size=crop_size,
                random_horizontal_flip=self.cfg.DATA.RANDOM_FLIP,
                inverse_uniform_sampling=self.cfg.DATA.INV_UNIFORM_SAMPLE,
            )
            label = self._labels[index]
            label = torch.FloatTensor(label)
            mask = self._labels_masks[index]
            mask = torch.FloatTensor(mask)
            frames = utils.pack_pathway_output(self.cfg, frames)

            return frames, label, mask, index, self._path_to_ant_videos[index]
        else:
            print(self._path_to_ant_videos[index])
            raise RuntimeError(
                "Failed to fetch video after {} retries.".format(
                    self._num_retries
                )
            )

    def __len__(self):
        """
        Returns:
            (int): the number of videos in the dataset.
        """

        return len(self._path_to_ant_videos)