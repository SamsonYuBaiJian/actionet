from builtins import int
import ai2thor.controller
import re
import time
import glob
import cv2
import os
from scene_config import set_initial_scene_config

def main(ai2thor_build_path, target_data_dir_for_frames, save_frames_dir, width, height):
    """
    Summary:
        Replays actions as a video and save frames.
    Args:
        ai2thor_build_path (string): Path of the custom Linux AI2-THOR Unity build file.
        target_data_dir_for_frames (string): Path of the folder containing only your target action data files to be converted to images, eg. /path/tp/actionet/dataset/1/.
        save_frames_dir (string): Path of folder to store saved frames.
        width (integer): Width of playback frame.
        height(integer): Height of playback frame.
    """
    controller = ai2thor.controller.Controller()
    controller.local_executable_path = ai2thor_build_path
    controller.start(player_screen_width=width,player_screen_height=height)
    event = controller.step(
                dict(action='AddThirdPartyCamera', rotation=dict(x=0, y=0, z=0), position=dict(x=0, z=0, y=0)))
    event.third_party_camera_frames
    files = [os.path.join(target_data_dir_for_frames, f) for f in os.listdir(target_data_dir_for_frames)]

    file_cnt = 0
    length = len(files)

    for name in files:
        with open(name) as f:
            task=f.read()

            # process action list
            task = task.replace('][', ',')
            task = task.replace('[','')
            task = task.replace(']','')
            task = task.replace("'", '')
            action_list =  task.split(",")
            action_list = [word.strip() for word in action_list]
            task = action_list[0]
            room = action_list[1]
            action_list.pop(0)
            action_list.pop(0)

            controller.reset(room)
            event = controller.step(dict(action='Initialize', gridSize=0.25, renderObjectImage="True"))
            event = set_initial_scene_config(event, task, controller)

            # check for random agent initial position for augmented data
            if 'TeleportFull' in action_list[0]:
                teleport = action_list[0].split('_')
                x = float(teleport[1])
                y = float(teleport[2])
                z = float(teleport[3])
                rot = float(teleport[4])
                event = controller.step(dict(action='TeleportFull', x=x, y=y, z=z, rotation=dict(x=0.0, y=rot, z=0.0), horizon=0))

            final_save_path = os.path.join(save_frames_dir, str(task) + '_' + str(room))
            if not os.path.exists(final_save_path):
                os.makedirs(final_save_path)

            action_cnt = 0
            frame_cnt = 0

            anglehandX = 0.0
            anglehandY = 0.0
            anglehandZ = 0.0

            for i in action_list:
                if not re.search('\d+', i):
                    if i == 'PickupObject' or i=='UseUpObject'or i=='EmptyLiquidFromObject' or i =='ToggleObjectOn' or i == 'ToggleObjectOff' or i== 'OpenObject' or i =='CloseObject' or i=='SliceObject' or i== 'BreakObject' or i== 'DirtyObject' or i=='CleanObject':
                        event = controller.step(dict(action=i, objectId=action_list[action_cnt+1]))
                    elif i == 'PutObject':
                        event = controller.step(dict(action=i, objectId=action_list[action_cnt+1], receptacleObjectId=action_list[action_cnt+2],forceAction=True))
                    elif i=='ThrowObject' or i=='PushObject' or i=='PullObject':
                        event = controller.step(dict(action=i, moveMagnitude=100.0))
                    elif i == 'FillObjectWithLiquid':
                        event = controller.step(dict(action=i, objectId=action_list[action_cnt + 1], fillLiquid=action_list[action_cnt + 2]))
                    elif i=='DropHandObject' or i=='Crouch' or i=='Stand':
                        event = controller.step(dict(action=i))
                    elif i=='RotateHandX':
                        anglehandX=anglehandX+30.0
                        event = controller.step(dict(action='RotateHand', x=anglehandX))
                    elif i=='RotateHandY':
                        anglehandY=anglehandY+30.0
                        event = controller.step(dict(action='RotateHand', y=anglehandY))
                    elif i=='RotateHandZ':
                        anglehandZ=anglehandZ+30.0
                        event = controller.step(dict(action='RotateHand', z=anglehandZ))
                    elif i=='MoveHandAhead' or i=='MoveHandBack' or i =='MoveHandLeft' or i=='MoveHandRight' or i=='MoveHandUp' or i=='MoveHandDown':
                        event = controller.step(dict(action=i, moveMagnitude=0.1))
                    elif i == 'MoveRight' or i == 'MoveAhead' or i == 'MoveLeft' or i == 'MoveBack' or i == 'RotateLeft' or i == 'RotateRight' or i == 'LookUp' or i == 'LookDown':
                        event = controller.step(dict(action=i))

                    frame_cnt += 1
                    cv2.imwrite(str(final_save_path)+'/'+str(frame_cnt)+ '.jpg',event.cv2img)

                action_cnt += 1

        file_cnt += 1
        f.close()
        print('File(s) done: ' + str(file_cnt) + '/' + str(length))


if __name__ == '__main__':
    with open('./settings.txt') as f:
        txt = f.readlines()
        f.close()
    my_dict = {}
    for t in txt:
        t = t.split('=')
        my_dict[t[0]] = t[1].strip('\n')

    main(my_dict['ai2thor_build_path'], my_dict['target_data_dir_for_frames'], my_dict['save_frames_dir'], int(my_dict['width']), int(my_dict['height']))