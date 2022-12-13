# python tools/short_term_anticipation/train_object_detector.py /media/dml/data40T/dataset/ego4d/FC/short_term_anticipation/annotations/train_coco.json /media/dml/data40T/dataset/ego4d/FC/short_term_anticipation/annotations/val_coco.json /media/dml/data40T/dataset/ego4d/FC/short_term_anticipation/data/object_frames/ /media/dml/data40T/dataset/ego4d/FC/short_term_anticipation/models/object_detector/
# train:
# python tools/short_term_anticipation/train_object_detector.py /media/dml/e5afa40a-df1a-4c60-8623-87e2a51c3a09/dataset/ego4d/FC/short_term_anticipation/annotations/train_coco.json /media/dml/e5afa40a-df1a-4c60-8623-87e2a51c3a09/dataset/ego4d/FC/short_term_anticipation/annotations/val_coco.json /media/dml/e5afa40a-df1a-4c60-8623-87e2a51c3a09/dataset/ego4d/FC/short_term_anticipation/data/object_frames/ /media/dml/e5afa40a-df1a-4c60-8623-87e2a51c3a09/dataset/ego4d/FC/short_term_anticipation/models/object_detector/
# val:
# python scripts/run_sta.py   --cfg configs/Ego4dShortTermAnticipation/SLOWFAST_32x1_8x4_R50.yaml     TRAIN.ENABLE False TEST.ENABLE True ENABLE_LOGGING False     CHECKPOINT_FILE_PATH /media/dml/data40T/dataset/ego4d/FC/short_term_anticipation/models/slowfast_model.ckpt     RESULTS_JSON /home/dml/GitCode/Ego4d_Forecasting/result/short_term_anticipation_results_val.json     CHECKPOINT_LOAD_MODEL_HEAD True     DATA.CHECKPOINT_MODULE_FILE_PATH ""     CHECKPOINT_VERSION ""     TEST.BATCH_SIZE 1 NUM_GPUS 1     EGO4D_STA.OBJ_DETECTIONS /media/dml/data40T/dataset/ego4d/FC/short_term_anticipation/data/object_detections.json     EGO4D_STA.ANNOTATION_DIR /media/dml/data40T/dataset/ego4d/HO/v1/annotations/     EGO4D_STA.RGB_LMDB_DIR /media/dml/data40T/dataset/ego4d/FC/short_term_anticipation/data/lmdb/     EGO4D_STA.TEST_LISTS "['fho_sta_test_unannotated.json']"
# test:
# mkdir -p short_term_anticipation/results
# python scripts/run_sta.py \
#     --cfg configs/Ego4dShortTermAnticipation/SLOWFAST_32x1_8x4_R50.yaml \
#     TRAIN.ENABLE False TEST.ENABLE True ENABLE_LOGGING False \
#     CHECKPOINT_FILE_PATH /media/dml/e5afa40a-df1a-4c60-8623-87e2a51c3a09/dataset/ego4d/FC/short_term_anticipation/models/slowfast_model.ckpt \
#     RESULTS_JSON result/short_term_anticipation_results_val.json \
#     CHECKPOINT_LOAD_MODEL_HEAD True \
#     DATA.CHECKPOINT_MODULE_FILE_PATH "" \
#     CHECKPOINT_VERSION "" \
#     TEST.BATCH_SIZE 1 NUM_GPUS 1 \
#     EGO4D_STA.OBJ_DETECTIONS /media/dml/e5afa40a-df1a-4c60-8623-87e2a51c3a09/dataset/ego4d/FC/short_term_anticipation/data/object_detections.json \
#     EGO4D_STA.ANNOTATION_DIR /media/dml/e5afa40a-df1a-4c60-8623-87e2a51c3a09/dataset/ego4d/FC/annotations/ \
#     EGO4D_STA.RGB_LMDB_DIR /media/dml/e5afa40a-df1a-4c60-8623-87e2a51c3a09/dataset/ego4d/FC/short_term_anticipation/data/lmdb/ \
#     EGO4D_STA.TEST_LISTS "['fho_sta_test_unannotated.json']"
# slowfast train:
# mkdir -p short_term_anticipation/models/slowfast_model/
# python scripts/run_sta.py \
#     --cfg configs/Ego4dShortTermAnticipation/SLOWFAST_32x1_8x4_R50.yaml \
#     EGO4D_STA.ANNOTATION_DIR /media/dml/e5afa40a-df1a-4c60-8623-87e2a51c3a09/dataset/ego4d/FC/annotations \
#     EGO4D_STA.RGB_LMDB_DIR /media/dml/e5afa40a-df1a-4c60-8623-87e2a51c3a09/dataset/ego4d/FC/short_term_anticipation/data/lmdb \
#     EGO4D_STA.OBJ_DETECTIONS /media/dml/e5afa40a-df1a-4c60-8623-87e2a51c3a09/dataset/ego4d/FC/short_term_anticipation/data/object_detections.json\
#     OUTPUT_DIR /home/dml/GitCode/Ego4d_Forecasting/short_term_anticipation/models/slowfast_model/
# eval the result
# python tools/short_term_anticipation/evaluate_short_term_anticipation_results.py result/short_term_anticipation_results_val.json /media/dml/e5afa40a-df1a-4c60-8623-87e2a51c3a09/dataset/ego4d/FC/annotations/fho_sta_val.json