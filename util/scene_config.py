import numpy as np
import math

def set_initial_scene_config(event, task, controller):
    """
    Summary:
        Set custom initial scene configurations for certain tasks.
    Args:
        event (ai2thor.controller.Controller().step() Event object): Contains metadata of current scene.
        task (string): Task to determine initial scene configuration.
        controller (ai2thor.controller.Controller()): AI2-THOR controller.
    Returns:
        ai2thor.controller.Controller().step() Event object: Contains metadata of current scene.
    """
    config_task_list = [
                'Wash Dishes',
                'Throw away cracked egg',
                'Throw away unused apple slice',
                'Pour away coffee in a cup',
                'Pour away water from pot',
                'Use laptop',
                'Throw away used tissuebox',
                'Turn off the table lamp or desk lamp',
                'Open Blinds',
                'Clean the bed',
                'Close the blinds',
                'Put off a candle',
                'Throw away used toilet roll and soap bottle',
                'Water the houseplant',
                'Clean the mirror',
                'Turn on all the floor lamp',
                'Wash dirty cloths'
            ]

    if task == config_task_list[0]:
        for obj in event.metadata['objects']:
            if obj['objectType'] == 'Plate' or obj['objectType'] == 'Bowl':
                target_id = obj['objectId']
                event = controller.step(
                    dict(action='SpecificToggleSpecificState', StateChange='DirtyObject', objectId=target_id))

    elif task == config_task_list[1]:
        for obj in event.metadata['objects']:
            if obj['objectType'] == 'Egg':
                target_id = obj['objectId']
                event = controller.step(
                    dict(action='SpecificToggleSpecificState', StateChange='BreakObject', objectId=target_id))

    elif task == config_task_list[2]:
        for obj in event.metadata['objects']:
            if obj['objectType'] == 'Apple':
                target_id = obj['objectId']
                event = controller.step(
                    dict(action='SpecificToggleSpecificState', StateChange='SliceObject', objectId=target_id))

    elif task == config_task_list[3]:
        for obj in event.metadata['objects']:
            if obj['objectType'] == 'Cup':
                target_id = obj['objectId']
                event = controller.step(
                    dict(action='SpecificToggleSpecificState', StateChange="FillObjectWithLiquid",
                        objectId=target_id, fillLiquid='coffee'))

    elif task == config_task_list[4]:
        for obj in event.metadata['objects']:
            if obj['objectType'] == 'Pot':
                target_id = obj['objectId']
                event = controller.step(
                    dict(action='SpecificToggleSpecificState', StateChange="FillObjectWithLiquid",
                        objectId=target_id, fillLiquid='water'))
    elif task == config_task_list[5]:
        for obj in event.metadata['objects']:
            if obj['objectType'] == 'Laptop':
                target_id = obj['objectId']
                event = controller.step(
                    dict(action='SpecificToggleSpecificState', StateChange="CloseObject", objectId=target_id))

    elif task == config_task_list[6]:
        for obj in event.metadata['objects']:
            if obj['objectType'] == 'TissueBox':
                target_id = obj['objectId']
                event = controller.step(
                    dict(action='SpecificToggleSpecificState', StateChange="UseUpObject", objectId=target_id))

    elif task == config_task_list[7]:
        for obj in event.metadata['objects']:
            if obj['objectType'] == 'DeskLamp':
                target_id = obj['objectId']
                event = controller.step(
                    dict(action='SpecificToggleSpecificState', StateChange="ToggleObjectOn", objectId=target_id))

    elif task == config_task_list[8]:
        for obj in event.metadata['objects']:
            if obj['objectType'] == 'Blinds':
                target_id = obj['objectId']
                event = controller.step(
                    dict(action='SpecificToggleSpecificState', StateChange="CloseObject", objectId=target_id))

    elif task == config_task_list[9]:
        for obj in event.metadata['objects']:
            if obj['objectType'] == 'Bed':
                target_id = obj['objectId']
                event = controller.step(
                    dict(action='SpecificToggleSpecificState', StateChange='DirtyObject', objectId=target_id))

    elif task == config_task_list[10]:
        for obj in event.metadata['objects']:
            if obj['objectType'] == 'Blinds':
                target_id = obj['objectId']
                event = controller.step(
                    dict(action='SpecificToggleSpecificState', StateChange="OpenObject", objectId=target_id))

    elif task == config_task_list[11]:
        for obj in event.metadata['objects']:
            if obj['objectType'] == 'Candle':
                target_id = obj['objectId']
                event = controller.step(
                    dict(action='SpecificToggleSpecificState', StateChange="ToggleObjectOn", objectId=target_id))

    elif task == config_task_list[12]:
        for obj in event.metadata['objects']:
            if obj['objectType'] == 'ToiletPaper' or obj['objectType'] == 'SoapBottle':
                target_id = obj['objectId']
                event = controller.step(
                    dict(action='SpecificToggleSpecificState', StateChange="UseUpObject", objectId=target_id))

    elif task == config_task_list[13]:
        for obj in event.metadata['objects']:
            if obj['objectType'] == 'WateringCan':
                target_id = obj['objectId']
                event = controller.step(
                    dict(action='SpecificToggleSpecificState', StateChange="FillObjectWithLiquid",
                        objectId=target_id, fillLiquid='water'))

    elif task == config_task_list[14]:
        for obj in event.metadata['objects']:
            if obj['objectType'] == 'Mirror':
                target_id = obj['objectId']
                event = controller.step(
                    dict(action='SpecificToggleSpecificState', StateChange="DirtyObject", objectId=target_id))

    elif task == config_task_list[15]:
        for obj in event.metadata['objects']:
            if obj['objectType'] == 'FloorLamp':
                target_id = obj['objectId']
                event = controller.step(
                    dict(action='SpecificToggleSpecificState', StateChange="ToggleObjectOff", objectId=target_id))

    elif task == config_task_list[16]:
        for obj in event.metadata['objects']:
            if obj['objectType'] == 'Cloth':
                target_id = obj['objectId']
                event = controller.step(
                    dict(action='SpecificToggleSpecificState', StateChange="DirtyObject", objectId=target_id))

    return event