mkdir -p data/stage2/
cd ../data/stage1/
kaggle competitions download -c <competition name> -f test_stage_2.csv
cd ..

#DATA PROCESSING
# The train/predict code will also call this script if it has not already been run on the relevant data.
python ./train_code/prepare_data.py --data_dir=data/stage1/ --output_dir=data/stage1_cleaned

#MODEL BUILD: There are three options to produce the solution.
1) very fast prediction
    a) runs in a few minutes
    b) uses precomputed neural network predictions
2) ordinary prediction
    a) expect this to run for 1-2 days
    b) uses binary model files
3) retrain models
    a) expect this to run about a week
    b) trains all models from scratch
    c) follow this with (2) to produce entire solution from scratch

shell command to run each build is below
#1) very fast prediction (overwrites comp_preds/sub1.csv and comp_preds/sub2.csv)
python ./predict_code/calibrate_model.py

#2) ordinary prediction (overwrites predictions in comp_preds directory)
sh ./predict_code/predict_models.sh

#3) retrain models (overwrites models in comp_model directory)
sh ./train_code/train_models.sh
