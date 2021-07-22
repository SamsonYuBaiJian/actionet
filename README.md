# ActioNet: An Interactive End-to-End Platform for Task-Based Data Collection and Augmentation in 3D Environments

ActioNet Paper: https://arxiv.org/abs/2010.01357

## Task-Based Dataset
It is created using **AI2-THOR** (https://ai2thor.allenai.org/). We have **made changes** to allow for the **customisation of initial scene settings (eg. object state) for some tasks**. The edited AI2-THOR can be cloned from https://github.com/SamsonYuBaiJian/ai2thor. The custom scene configurations can be found in `./util/scene_config.py`.

Our **human annotated dataset** can be found in the `./dataset/{collection_instance}` folders.

Each **data file** has the naming convention of `./dataset/{collection_instance}/{task}_{floor_plan}`. In each file, there are **two lists**:
- First list: `[task, floor_plan]`
- Second list: `[first_action, second_action, ..., last_action]`

The `./dataset_info/task_descriptions` folder contains the **descriptions of the tasks for each collection instance**.

The `./dataset_info/user_tasks` folder contains the **collection instances and tasks that each user is in charge of**, for a total of **10 users**.

The AI2-THOR agent has a default configuration of `grid_size=0.25`, meaning that each grid block has the size of 0.25 meters.

## Dataset Statistics
Dataset statistics are obtained from running `python3 ./util/get_stats.py`.

The statistics can be found in `./stats.txt`.

## System Requirements
- Linux (tested on Ubuntu 18.04) for using the custom AI2-THOR Unity build
- **Python 3.6**
- External Python libraries: ai2thor, keyboard, opencv-python, pillow
- Unity 2018.3.6f1

## Script Configurations
You can set configurations for custom directories and AI2-THOR settings in `./settings.txt` in the `{setting}={setting_choice}` format.
- `actionet_path`: Path to **ActioNet root directory**
- `ai2thor_build_path`: Path to **custom AI2-THOR Linux build**, from `https://github.com/SamsonYuBaiJian/ai2thor`, eg. `./ai2thor/unity/Builds/linux.x86_64`
- `target_data_dir_for_frames`: Path to **folder of data files** for creating frames with `./util/replay_and_save_frames.py`, eg. `./dataset/1`
- `save_frames_dir`: Path to **save frames** created with `./util/replay_and_save_frames.py`
- `save_augmented_data_dir`: Path to **save augmented data** created with `./util/augment_data.py`, eg. `./augmented_dataset`
- `target_augmentation_file`: Path to **specific data file for data augmentation** with `./util/augment_data.py`, eg. `./dataset/1/Make coffee_FloorPlan1`
- `random_start`: Whether to initialise agent at a **random position for data augmentation**, eg. True or False
- `seed`: Seed for randomising agent location for data augmentation
- `width`: Width of AI2-THOR frame for data augmentation and saving frames
- `height`: Height of AI2-THOR frame for data augmentation and saving frames

## Creating Images from Data
The `./util/replay_and_save_frames.py` file is used to **replay the actions** in the dataset as a series of frames, and **save the frames** in a chosen directory.

Settings can be found in `./settings.txt`.

Some **samples** can be found in the `./saved_frames` and `./augmented_saved_frames` folders.

## Data Augmentation
**Sample data files** can be found in the `./augmented_dataset` folder. If a data file has **'TeleportFull...'** as its first action, it means the **agent's starting position was randomised**.

The **data files that can be augmented** are listed in `./augmentable_data_files.txt`.

Data files that have **hand movements, 'ThrowObject', 'PullObject' or 'PushObject' are not augmentable**.

## Future Work
- Do a final examination of the human annotated and augmented datasets
- Explore interesting use cases

## If you use ActioNet, please cite the our paper:
@inproceedings{duan2020actionet,
    title={Actionet: An Interactive End-To-End Platform For Task-Based Data Collection And Augmentation In 3D Environment},
    author={Duan, Jiafei and Yu, Samson and Tan, Hui Li and Tan, Cheston},
    booktitle={2020 IEEE International Conference on Image Processing (ICIP)},
    pages={1566--1570},
    year={2020},
    organization={IEEE}
}


