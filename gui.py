import tkinter as tk
import os
import ai2thor.controller
from PIL import Image, ImageTk
import imageio
import keyboard
import threading
import queue
import time
import re
import operator
from tkinter.ttk import *
from tkinter import messagebox
import csv
import cv2

class Gui():
    """
    Set overall GUI.
    """

    def __init__(self, root):
        """Initialise GUI."""
        # Create queues
        stage_queue = queue.Queue()
        scene_queue = queue.Queue()
        demo_queue = queue.Queue()
        frame_queue = queue.Queue()
        object_queue = queue.Queue()
        input_queue = queue.Queue()
        # Show status
        status = tk.Label(root, text="STATUS: Entering user ID...\n")
        status.pack(side="top", fill="x")
        # Set consistent frame
        container = tk.Frame(root)
        container.pack(side="top", fill="both", expand=True)
        # Instantiate AI2-THOR with queues
        ai2_thor = AI2THOR(stage_queue, scene_queue, demo_queue, frame_queue, object_queue, input_queue)
        ai2_thor_thread = threading.Thread(target=lambda: ai2_thor.run())
        ai2_thor_thread.start()
        # Set initial page to choose task page
        user_id = UserIDPage(root)
        user_id.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
        user_id.show(root, container, status, user_id, None, None, None, None, None, stage_queue, scene_queue,
                     demo_queue, frame_queue,
                     object_queue, input_queue)


class UserIDPage(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)

    def show(self, root, container, status, user_id, choose_task, demo, do_action, do_input, review, stage_queue,
             scene_queue, demo_queue,
             frame_queue, object_queue, input_queue):
        # do not have to clear unused pages, since we only use this page once
        id_list = []
        no_of_people = 200
        for i in range(no_of_people):
            id_list.append(str(i + 1))

        user_num_frame = tk.Frame(self)
        user_num_frame.pack(side="top")
        user_num_text = tk.Label(self, text="Enter your user ID:")
        user_num_text.pack(in_=user_num_frame, side="left")
        user_num_text.config(font=('Courier', '20'))
        user_num_input = tk.Entry(self)
        user_num_input.pack(in_=user_num_frame, side="left")
        check_id_validity_button = tk.Button(self, text="BEGIN", font=('Courier', '19'),
                                             command=lambda: self.check_id_validity(user_num_input.get(), id_list, root,
                                                                                    container, status,
                                                                                    user_id, choose_task, None, None,
                                                                                    None, None, stage_queue,
                                                                                    scene_queue, demo_queue,
                                                                                    frame_queue,
                                                                                    object_queue, input_queue))
        check_id_validity_button.pack(side="top")
        self.lift()

    def check_id_validity(self, user_id, id_list, root, container, status, user_num, choose_task, choose_action, do_action,
                          do_input, review, stage_queue, scene_queue, demo_queue,
                          frame_queue, object_queue, input_queue):
        if str(user_id) not in id_list:
            # id not in list --> show popup error message
            messagebox.showerror("Error",
                                 "Please make sure you enter a valid user ID, from 1 to " + id_list[-1] + ".")
        else:
            # valid id --> move to task choosing page
            if not os.path.exists("saved-tasks/" + str(user_id)):
                os.mkdir("saved-tasks/" + str(user_id))
            with open('saved-tasks/user.txt', 'w') as f:
                f.truncate(0)
                f.write(str(user_id))
            f.close()
            choose_task = ChooseTaskPage(root)
            choose_task.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
            choose_task.show(root, container, user_id, status, None,
                             user_num, choose_task, choose_action, do_action,
                             do_input, review, stage_queue, scene_queue, demo_queue, frame_queue,
                             object_queue, input_queue)


class ChooseTaskPage(tk.Frame):
    """
    Set choose task page GUI.
    """

    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)

    def show(self, root, container, user_id, status, task, user_num, choose_task, demo, do_action, do_input, review,
             stage_queue, scene_queue,
             demo_queue, frame_queue, object_queue, input_queue):
        # Clear unused pages
        if demo != None:
            demo.destroy()
        if do_action != None:
            do_action.destroy()
        if do_input != None:
            do_input.destroy()
        if user_num != None:
            user_num.destroy()
        if review != None:
            review.destroy()
        stage_queue.put('choose_task')
        self.scene_queue = scene_queue
        self.frame_queue = frame_queue
        self.user_id=user_id
        status['text'] = "STATUS: Choosing task...\n"
        # Show initial frame
        self.ai2thor_frame = tk.Label(self)
        self.get_and_set_frame()
        self.ai2thor_frame.pack(side="top")

        # Select tasks for specific users --> using 'user_id'
        self.SCENES = []
        self.TASKS = []

        completed_tasks = os.listdir('saved-tasks/' + str(self.user_id))
        completed_tasks = [x.split('_')[0] for x in completed_tasks]
        if task is not None:
            completed_tasks.append(task)

        with open('resources/tasks/' + str(self.user_id)+'.csv', newline='') as csvfile:
            csv_data = csv.reader(csvfile)
            next(csv_data)
            for row in csv_data:
                task_data = row[0]
                task_data = task_data.split("_")[0]
                if task_data not in completed_tasks:
                    self.TASKS.append(task_data)

                    scene = row[0]
                    scene = scene.split('_')[-2]
                    self.SCENES.append(scene)

        task_frame = tk.Frame(self)
        task_frame.pack(side="top")
        task_text = tk.Label(self, text="Choose task:")
        task_text.pack(in_=task_frame, side="left")
        task_text.config(font=('Courier', '20'))
        self.task = tk.StringVar(self)
        self.task.set(self.TASKS[0])

        # set initial scene
        self.scene = self.SCENES[0]
        self.scene_queue.put(self.scene)

        self.task.trace("w", self.send_scene)
        task_options = Combobox(self, textvariable=self.task, state="readonly", values=self.TASKS, font=('Courier', '20'))
        task_options.pack(in_=task_frame, side="left")
        # Create start task button
        demo = DemoPage(root)
        demo.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
        demo_button = tk.Button(self, text="WATCH DEMO", font=('Courier', '19'),
                                command=lambda: demo.show(root, container, user_id, status, self.task.get(),
                                                          self.scene, choose_task, demo, None,
                                                          None, None, stage_queue, scene_queue, demo_queue, frame_queue,
                                                          object_queue, input_queue,
                                                          self.ai2thor_frame.image))
        demo_button.pack(side="bottom", fill="x", expand=False)
        self.lift()

    def send_scene(self, *args):
        """Get scene in the scene options and send to scene_queue."""
        index = self.TASKS.index(self.task.get())
        self.scene = self.SCENES[index]
        self.scene_queue.put(self.scene)

    def get_and_set_frame(self):
        """Get first frame in the frame_queue, if any, and set the GUI frame to that frame."""
        try:
            frame = self.frame_queue.get(0)
            self.ai2thor_frame.configure(image=frame)
            self.ai2thor_frame.image = frame
            self.after(1, self.get_and_set_frame)
        except queue.Empty:
            self.after(1, self.get_and_set_frame)


class DemoPage(tk.Frame):
    """
    Set choose action page GUI.
    """

    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)

    def show(self, root, container, user_id, status, task, scene, choose_task, demo, do_action, do_input, review,
             stage_queue,
             scene_queue, demo_queue, frame_queue, object_queue, input_queue, initial_frame):
        """Show information for action."""
        # Clear unused pages
        if choose_task != None:
            choose_task.destroy()
        if do_action != None:
            do_action.destroy()
        if do_input != None:
            do_input.destroy()
        if review != None:
            review.destroy()

        self.demo_queue = demo_queue

        # write task and scene settings to draw it later
        with open('saved-tasks/settings.txt', 'w') as f:
            f.truncate(0)
            f.write(task + "\n")
            f.write("FloorPlan" + scene)
        f.close()

        # set initial config for scene
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

        if task in config_task_list:
            index = config_task_list.index(task)
        else:
            index = -1
        scene_queue.put(int(index))

        stage_queue.put('demo')

        # Show status
        status['text'] = "STATUS: Watching the demo video...\n"

        instruction = "Demo task: Fill up water." + "\nDemo instruction: Find an empty mug, and put it under running water."
        instruction_label = tk.Label(self, text=instruction, wraplength=700)
        instruction_label.pack(side="top")
        instruction_label.config(font=("Courier Bold", 14))

        # show demo video
        self.demo_frame = tk.Label(self)
        self.get_and_set_demo_video()
        self.demo_frame.pack(side="top")

        do_action = DoActionPage(root)
        do_action.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
        start_action_button = tk.Button(self, text="START TASK", font=('Courier', '19'),
                                        command=lambda: do_action.show(root, container, user_id, status, task, scene,
                                                                       None, demo,
                                                                       do_action, None, None, stage_queue, scene_queue,
                                                                       demo_queue,
                                                                       frame_queue, object_queue, input_queue,
                                                                       initial_frame, ))
        start_action_button.pack(side="bottom", fill="x", expand=False)
        # Show page
        self.lift()

    def get_and_set_demo_video(self):
        """Get first frame in the frame_queue, if any, and set the GUI frame to that frame."""
        try:
            frame = self.demo_queue.get(0)
            frame = ImageTk.PhotoImage(frame)
            self.demo_frame.configure(image=frame)
            self.demo_frame.image = frame
            self.after(1, self.get_and_set_demo_video)
        except queue.Empty:
            self.after(1, self.get_and_set_demo_video)


class DoActionPage(tk.Frame):
    """
    Choose do action page GUI.
    """

    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)

    def show(self, root, container, user_id, status, task, scene, choose_task, demo, do_action,
             do_input, review, stage_queue, scene_queue, demo_queue, frame_queue, object_queue, input_queue,
             initial_frame):
        # Clear unused pages
        if demo != None:
            demo.destroy()
        if choose_task != None:
            choose_task.destroy()
        if do_input != None:
            do_input.destroy()
        if review != None:
            review.destroy()
        self.frame_queue = frame_queue
        self.object_queue = object_queue
        self.stage_queue = stage_queue
        stage_queue.put('do_action')
        # Show status
        status[
            'text'] = "STATUS: Doing '" + task + "' task in FloorPlan" + scene + "...\n"

        # Show frame(s)
        self.ai2thor_frame = tk.Label(self)
        self.ai2thor_frame.configure(image=initial_frame)
        self.ai2thor_frame.image = initial_frame
        self.ai2thor_frame.pack(side="top")
        self.get_and_set_frame()

        # change instruction according to 'task'
        with open('resources/tasks/' + str(user_id)+'.csv', newline='') as csvfile:
            csv_data = csv.reader(csvfile)
            next(csv_data)
            for row in csv_data:
                if task == row[0].split('_')[0]:
                    content = row[1]
                    break
        instruction = "\nINSTRUCTIONS: " + content
        instruction_label = tk.Label(self, text=instruction)
        instruction_label = tk.Label(self, text=instruction,wraplength=700)
        instruction_label.pack(side="top")

        # show keyboard
        keyboard = Image.open("resources/keyboard-control.png")
        keyboard = keyboard.resize((990, 280))
        keyboard_render = ImageTk.PhotoImage(keyboard)
        keyboard_label = Label(self, image=keyboard_render)
        keyboard_label.image = keyboard_render
        keyboard_label.place(x=100, y=620)

        # clock = Label(self)
        # clock.pack(side="bottom")
        # def tick():
        #     global time1
        #     # get the current local time from the PC
        #     time2 = time.strftime('%H:%M:%S')
        #     # if time string has changed, update it
        #     if time2 != time1:
        #         time1 = time2
        #         clock.config(text="Time:"+time2)
        #     # calls itself every 200 milliseconds
        #     # to update the time display as needed
        #     # could use >200 ms, but display gets jerky
        #     clock.after(200, tick)
        # tick()
        # labels can be text or images

        # Object interaction button
        do_input = DoInputPage(root)
        do_input.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
        object_interaction_button = tk.Button(self, text="Interact with an object", font=('Courier', '20'),
                                              command=lambda: do_input.show(root, container, user_id, status, task,
                                                                            scene, None, None, do_action,
                                                                            do_input, review, stage_queue, scene_queue,
                                                                            demo_queue,
                                                                            frame_queue, object_queue, input_queue,
                                                                            self.ai2thor_frame.image))
        object_interaction_button.pack(side="top", expand=False)

        # Create finish task button
        review = ReviewPage(root)
        review.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
        finish_task_button = tk.Button(self, text="FINISH AND REVIEW TASK",font=('Courier', '19'),
                                       command=lambda: review.show(root, container, user_id, status, task, scene, None,
                                                                   None,
                                                                   do_action, do_input, review, stage_queue,
                                                                   scene_queue, demo_queue,
                                                                   frame_queue, object_queue, input_queue))
        finish_task_button.pack(side="bottom", fill="x", expand=False)

        self.lift()

    def get_and_set_frame(self):
        """Get first frame in the frame_queue, if any, and set the GUI frame to that frame."""
        try:
            frame = self.frame_queue.get(0)
            self.ai2thor_frame.configure(image=frame)
            self.ai2thor_frame.image = frame
            self.after(1, self.get_and_set_frame)
        except queue.Empty:
            self.after(1, self.get_and_set_frame)


class DoInputPage(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)

    def show(self, root, container, user_id, status, task, scene, choose_task, demo, do_action,
             do_input, review, stage_queue, scene_queue, demo_queue, frame_queue, object_queue, input_queue,
             initial_frame):
        # Clear unused pages
        if demo != None:
            demo.destroy()
        if choose_task != None:
            choose_task.destroy()
        if do_action != None:
            do_action.destroy()
        if review != None:
            review.destroy()
        # Send stage update to AI2-THOR
        stage_queue.put('get_instance_obj')
        self.frame_queue = frame_queue
        self.object_queue = object_queue
        while True:
            try:
                object_list = self.object_queue.get(0)
                break
            except queue.Empty:
                pass
        self.input_queue = input_queue
        # Change status
        status[
            'text'] = "STATUS: Interacting with object for '" + task + "' task in FloorPlan" + scene + "...\n"
        # Show initial frame
        self.ai2thor_frame = tk.Label(self)
        self.ai2thor_frame.configure(image=initial_frame)
        self.ai2thor_frame.image = initial_frame
        self.ai2thor_frame.pack(side="top")
        # Show interaction action choices
        input_action_frame = tk.Frame(self)
        input_action_frame.pack(side="top")
        input_action_text = tk.Label(self, text="Choose interaction:")
        input_action_text.pack(in_=input_action_frame, side="left")
        input_action_text.config(font=('Courier', '20'))
        INPUT_ACTIONS = [
            "Break",
            "Clean",
            "Close",
            "Dirty",
            "Drop",
            "Empty",
            "Fill",
            "Open",
            "Pick up",
            "Used up",
            "Pull",
            "Push",
            "Put down",
            "Slice",
            "Stand",
            "Crouch",
            "Throw",
            "Toggle off",
            "Toggle on",
        ]
        self.input_actions = tk.StringVar(self)
        self.input_actions.set(INPUT_ACTIONS[0])
        self.input_actions.trace("w", self.configure_buttons)
        input_actions_options = Combobox(self, textvariable=self.input_actions, state="readonly", values=INPUT_ACTIONS,
                                         font=('Courier', '20'))
        input_actions_options.pack(in_=input_action_frame, side="left")
        # Show possible target objects
        self.target_object_frame = tk.Frame(self)
        self.target_object_frame.pack(side="top")
        self.target_object_text = tk.Label(self, text="Choose target object:")
        self.target_object_text.pack(in_=self.target_object_frame, side="left")
        self.target_object_text.config(font=('Courier', '20'))
        # Show possible target objects to PUT DOWN
        self.put_down_target_object_frame = tk.Frame(self)
        self.put_down_target_object_frame.pack(side="top")
        self.put_down_target_object_text = tk.Label(self, text="Choose location:")
        self.put_down_target_object_text.pack(in_=self.put_down_target_object_frame, side="left")
        self.put_down_target_object_frame.pack_forget()
        self.put_down_target_object_text.config(font=('Courier', '20'))

        # change instruction according to 'task'
        with open('resources/tasks/' + str(user_id)+'.csv', newline='') as csvfile:
            csv_data = csv.reader(csvfile)
            next(csv_data)
            for row in csv_data:
                if task == row[0].split('_')[0]:
                    content = row[1]
                    break
        instruction = "\nINSTRUCTIONS: " + content
        instruction_label = tk.Label(self, text=instruction)
        instruction_label = tk.Label(self, text=instruction,wraplength=700)
        instruction_label.pack(side="bottom")

        # clock = Label(self)
        # clock.pack(side="bottom")
        # def tick():
        #     global time1
        #     # get the current local time from the PC
        #     time2 = time.strftime('%H:%M:%S')
        #     # if time string has changed, update it
        #     if time2 != time1:
        #         time1 = time2
        #         clock.config(text="Time:" + time2)
        #     # calls itself every 200 milliseconds
        #     # to update the time display as needed
        #     # could use >200 ms, but display gets jerky
        #     clock.after(200, tick)
        # tick()
        LIQUIDS = [
            'coffee',
            'water',
            'wine'
        ]
        # Show possible liquids to FILL a target object with
        self.fill_target_object_frame = tk.Frame(self)
        self.fill_target_object_frame.pack(side="top")
        self.fill_target_object_text = tk.Label(self, text="Choose liquid:")
        self.fill_target_object_text.pack(in_=self.fill_target_object_frame, side="left")
        self.fill_target_object_text.config(font=('Courier', '20'))
        self.fill_target_object_frame.pack_forget()

        liquids = tk.StringVar(self)
        liquids.set(LIQUIDS[0])
        liquid_options = Combobox(self, textvariable=liquids, state="readonly", values=LIQUIDS, font=('Courier', '20'))
        liquid_options.pack(in_=self.fill_target_object_frame, side="left")
        # Get list of objects from AI2-THOR instance segmentation for target objects
        object_list.sort()
        OBJECTS = object_list
        self.objects = tk.StringVar(self)
        self.objects.set(OBJECTS[0])
        self.objects.trace("w", self.send_object_emphasis)
        objects_options = Combobox(self, textvariable=self.objects, state="readonly", values=OBJECTS,
                                   font=('Courier', '20'))
        objects_options.pack(in_=self.target_object_frame, side="left")
        # Also use list of objects from AI2-THOR instance segmentation for put down
        object_list.sort()
        OBJECTS = object_list
        self.object_locations = tk.StringVar(self)
        self.object_locations.set(OBJECTS[0])
        objects_location_options = Combobox(self, textvariable=self.object_locations, state="readonly", values=OBJECTS,
                                            font=('Courier', '20'))
        objects_location_options.pack(in_=self.put_down_target_object_frame, side="left")
        # Create finish interaction button
        do_action = DoActionPage(root)
        do_action.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
        finish_action_button = tk.Button(self, text="INTERACT", font=('Courier', '19'),
                                         command=lambda: self.after_input_before_action(root, container, user_id,
                                                                                        status, task,
                                                                                        scene,
                                                                                        None, None, do_action, do_input,
                                                                                        review,
                                                                                        stage_queue, scene_queue,
                                                                                        demo_queue,
                                                                                        frame_queue, object_queue,
                                                                                        self.input_queue, initial_frame,
                                                                                        self.input_actions.get(),
                                                                                        self.objects.get(),
                                                                                        liquids.get(),
                                                                                        self.object_locations.get()))
        finish_action_button.pack(side="bottom", fill="x", expand=False)
        self.get_and_set_frame()
        self.lift()

    def after_input_before_action(self, root, container, user_id, status, task, scene, choose_task,
                                  demo, do_action, do_input, review, stage_queue, scene_queue, demo_queue, frame_queue,
                                  object_queue, input_queue, initial_frame, input_action,
                                  target_interaction_object, fill_liquid, put_object_location):
        stage_queue.put('do_input')
        input_queue.put(['interaction', input_action, target_interaction_object, fill_liquid, put_object_location])
        do_action.show(root, container, user_id, status, task, scene, None, None, do_action, do_input, None,
                       stage_queue, scene_queue, demo_queue, frame_queue, object_queue, self.input_queue, initial_frame)

    def send_object_emphasis(self, *args):
        """
        Send objectId to be emphasised and get frame in return.
        """
        # Show emphasis on selected object to let user know which object is selected
        self.input_queue.put(['emphasis', self.objects.get()])

    def get_and_set_frame(self):
        try:
            frame = self.frame_queue.get(0)
            self.ai2thor_frame.configure(image=frame)
            self.ai2thor_frame.image = frame
            self.after(1, self.get_and_set_frame)
        except queue.Empty:
            self.after(1, self.get_and_set_frame)

    def configure_buttons(self, *args):
        """
        Hide or show buttons depending on needs.
        """
        interaction = self.input_actions.get()
        if interaction == 'Drop' or interaction == 'Throw' or interaction== 'Stand' or interaction=='Crouch':
            self.target_object_frame.pack_forget()
            self.put_down_target_object_frame.pack_forget()
            self.fill_target_object_frame.pack_forget()
        elif interaction == 'Fill':
            self.target_object_frame.pack()
            self.put_down_target_object_frame.pack_forget()
            self.fill_target_object_frame.pack()
        elif interaction == 'Put down':
            self.target_object_frame.pack()
            self.put_down_target_object_frame.pack()
            self.fill_target_object_frame.pack_forget()
        else:
            self.target_object_frame.pack()
            self.put_down_target_object_frame.pack_forget()
            self.fill_target_object_frame.pack_forget()


class ReviewPage(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)

    def show(self, root, container, user_id, status, task, scene, choose_task, demo, do_action,
             do_input, review, stage_queue, scene_queue, demo_queue, frame_queue, object_queue, input_queue):
        # Clear unused pages
        if demo != None:
            demo.destroy()
        if choose_task != None:
            choose_task.destroy()
        if do_action != None:
            do_action.destroy()
        if do_input != None:
            do_input.destroy()

        stage_queue.put('review')
        status['text'] = "STATUS: Reviewing actions for '" + task + "' task for FloorPlan" + scene + "...\n"

        self.frame_queue = frame_queue

        # show replay video
        self.ai2thor_frame = tk.Label(self)
        self.ai2thor_frame.pack(side="top")
        self.get_and_set_frame()

        choose_task = ChooseTaskPage(root)
        choose_task.place(in_=container, x=0, y=0, relwidth=1, relheight=1)

        save_button = tk.Button(self, text="SAVE TASK",
                                command=lambda: self.save_list(root, container, user_id, status, task, choose_task, None,
                                                               None, None, review, stage_queue, scene_queue, demo_queue,
                                                               frame_queue, object_queue, input_queue))
        save_button.pack(side="bottom", fill="x", expand=False)

        redo_task_button = tk.Button(self, text="REDO TASK",
                                       command=lambda: choose_task.show(root, container, user_id, status, None, None,
                                                                        choose_task, None, None,
                                                                        None, review, stage_queue, scene_queue,
                                                                        demo_queue,
                                                                        frame_queue, object_queue, input_queue))
        redo_task_button.pack(side="bottom", fill="x", expand=False)

        self.lift()

    def save_list(self, root, container, user_id, status, task, choose_task, demo,
                  do_action, do_input, review, stage_queue, scene_queue, demo_queue,
                  frame_queue, object_queue, input_queue):
        stage_queue.put("save")
        choose_task.show(root, container, user_id, status, task, None, choose_task, demo,
                         do_action, do_input, review, stage_queue, scene_queue, demo_queue,
                         frame_queue, object_queue, input_queue)

    def get_and_set_frame(self):
        """Get first frame in the frame_queue, if any, and set the GUI frame to that frame."""
        try:
            frame = self.frame_queue.get(0)
            self.ai2thor_frame.configure(image=frame)
            self.ai2thor_frame.image = frame
            self.after(1, self.get_and_set_frame)
        except queue.Empty:
            self.after(1, self.get_and_set_frame)


class AI2THOR():
    def __init__(self, stage_queue, scene_queue, demo_queue, frame_queue, object_queue, input_queue):
        self.stage_queue = stage_queue
        self.scene_queue = scene_queue
        self.demo_queue = demo_queue
        self.frame_queue = frame_queue
        self.object_queue = object_queue
        self.input_queue = input_queue

    def run(self):
        """Run AI2-THOR."""
        controller = ai2thor.controller.Controller()
        controller.local_executable_path = "/home/user/ai2thor/unity/unity/Builds/linux.x86_64"
        controller.start(player_screen_width=1000,
                         player_screen_height=500)
        anglehandx = 0.0
        anglehandy = 0.0
        anglehandz = 0.0
        # Set initial stage to None
        stage = None
        while True:
            # Check which stage the user is at
            # Sleep to prevent this from being too fast
            time.sleep(0.005)
            # Try to get stage from stage_queue
            try:
                stage = self.stage_queue.get(0)
            except queue.Empty:
                pass
            if stage == 'choose_task':
                # reset action list
                self.action_list = []
                try:
                    scene = self.scene_queue.get(0)
                    controller.reset('FloorPlan' + scene)
                    event = controller.step(dict(action='Initialize', gridSize=0.25, renderObjectImage="True"))
                    # Send frame to GUI
                    ai2thor_frame = ImageTk.PhotoImage(Image.fromarray(event.frame))
                    self.send_frame(ai2thor_frame)
                except queue.Empty:
                    continue
            elif stage == 'demo':
                # reset video demo queue
                with self.demo_queue.mutex:
                    self.demo_queue.queue.clear()
                # send demo video frames
                video_name = "resources/demo.mp4"  # This is your video file path
                video = imageio.get_reader(video_name)

                for frame in video.iter_data():
                    # see whether initial scene config is ready
                    try:
                        scene_config = self.scene_queue.get(0)
                        target_id = None
                        if scene_config == -1:
                            pass
                        elif scene_config == 0:
                            for obj in event.metadata['objects']:
                                if obj['objectType'] == 'Plate' or obj['objectType'] == 'Bowl':
                                    target_id = obj['objectId']
                                    event = controller.step(dict(action='SpecificToggleSpecificState', StateChange='DirtyObject', objectId=target_id))
                        elif scene_config == 1:
                            for obj in event.metadata['objects']:
                                if obj['objectType'] == 'Egg':
                                    target_id = obj['objectId']
                                    event = controller.step(dict(action='SpecificToggleSpecificState', StateChange='BreakObject', objectId=target_id))
                        elif scene_config == 2:
                            for obj in event.metadata['objects']:
                                if obj['objectType'] == 'Apple':
                                    target_id = obj['objectId']
                                    event = controller.step(dict(action='SpecificToggleSpecificState', StateChange='SliceObject', objectId=target_id))
                        elif scene_config == 3:
                            for obj in event.metadata['objects']:
                                if obj['objectType'] == 'Cup':
                                    target_id = obj['objectId']
                                    event = controller.step(dict(action='SpecificToggleSpecificState', StateChange="FillObjectWithLiquid", objectId=target_id, fillLiquid='coffee'))
                        elif scene_config == 4:
                            for obj in event.metadata['objects']:
                                if obj['objectType'] == 'Pot':
                                    target_id = obj['objectId']
                                    event = controller.step(dict(action='SpecificToggleSpecificState', StateChange="FillObjectWithLiquid", objectId=target_id, fillLiquid='water'))
                        elif scene_config == 5:
                            for obj in event.metadata['objects']:
                                if obj['objectType'] == 'Laptop':
                                    target_id = obj['objectId']
                                    event = controller.step(dict(action='SpecificToggleSpecificState', StateChange="CloseObject", objectId=target_id))
                        elif scene_config == 6:
                            for obj in event.metadata['objects']:
                                if obj['objectType'] == 'TissueBox':
                                    target_id = obj['objectId']
                                    event = controller.step(dict(action='SpecificToggleSpecificState', StateChange="UseUpObject", objectId=target_id))
                        elif scene_config == 7:
                            for obj in event.metadata['objects']:
                                if obj['objectType'] == 'DeskLamp':
                                    target_id = obj['objectId']
                                    event = controller.step(dict(action='SpecificToggleSpecificState', StateChange="ToggleObjectOn", objectId=target_id))
                        elif scene_config == 8:
                            for obj in event.metadata['objects']:
                                if obj['objectType'] == 'Blinds':
                                    target_id = obj['objectId']
                                    event = controller.step(dict(action='SpecificToggleSpecificState', StateChange="CloseObject", objectId=target_id))
                        elif scene_config == 9:
                            for obj in event.metadata['objects']:
                                if obj['objectType'] == 'Bed':
                                    target_id = obj['objectId']
                                    event = controller.step(dict(action='SpecificToggleSpecificState', StateChange='DirtyObject', objectId=target_id))
                        elif scene_config == 10:
                            for obj in event.metadata['objects']:
                                if obj['objectType'] == 'Blinds':
                                    target_id = obj['objectId']
                                    event = controller.step(dict(action='SpecificToggleSpecificState', StateChange="OpenObject", objectId=target_id))
                        elif scene_config == 11:
                            for obj in event.metadata['objects']:
                                if obj['objectType'] == 'Candle':
                                    target_id = obj['objectId']
                                    event = controller.step(dict(action='SpecificToggleSpecificState', StateChange="ToggleObjectOn", objectId=target_id))
                        elif scene_config == 12:
                            for obj in event.metadata['objects']:
                                if obj['objectType'] == 'ToiletPaper' or obj['objectType'] == 'SoapBottle':
                                    target_id = obj['objectId']
                                    event = controller.step(dict(action='SpecificToggleSpecificState', StateChange="UseUpObject", objectId=target_id))
                        elif scene_config == 13:
                            for obj in event.metadata['objects']:
                                if obj['objectType'] == 'WateringCan':
                                    target_id = obj['objectId']
                                    event = controller.step(dict(action='SpecificToggleSpecificState', StateChange="FillObjectWithLiquid", objectId=target_id, fillLiquid='water'))
                        elif scene_config == 14:
                            for obj in event.metadata['objects']:
                                if obj['objectType'] == 'Mirror':
                                    target_id = obj['objectId']
                                    event = controller.step(dict(action='SpecificToggleSpecificState', StateChange="DirtyObject", objectId=target_id))
                        elif scene_config == 15:
                            for obj in event.metadata['objects']:
                                if obj['objectType'] == 'FloorLamp':
                                    target_id = obj['objectId']
                                    event = controller.step(dict(action='SpecificToggleSpecificState', StateChange="ToggleObjectOff", objectId=target_id))
                        elif scene_config == 16:
                            for obj in event.metadata['objects']:
                                if obj['objectType'] == 'Cloth':
                                    target_id = obj['objectId']
                                    event = controller.step(dict(action='SpecificToggleSpecificState', StateChange="DirtyObject", objectId=target_id))

                        ai2thor_frame = ImageTk.PhotoImage(Image.fromarray(event.frame))
                        self.send_frame(ai2thor_frame)
                    except:
                        # to check for user skipping demo video
                        try:
                            stage = self.stage_queue.get(0)
                            break
                        except queue.Empty:
                            frame = Image.fromarray(frame).resize((880, 880))
                            self.demo_queue.put(frame)
                            time.sleep(.03)
            elif stage == 'do_action':
                # Send frame(s) to GUI
                if keyboard.is_pressed('right'):
                    event = controller.step(dict(action='MoveRight'))
                    ai2thor_frame = ImageTk.PhotoImage(Image.fromarray(event.frame))
                    self.send_frame(ai2thor_frame)
                    self.action_list.append("MoveRight")
                elif keyboard.is_pressed('up'):
                    event = controller.step(dict(action='MoveAhead'))
                    ai2thor_frame = ImageTk.PhotoImage(Image.fromarray(event.frame))
                    self.send_frame(ai2thor_frame)
                    self.action_list.append("MoveAhead")
                elif keyboard.is_pressed('down'):
                    event = controller.step(dict(action='MoveBack'))
                    ai2thor_frame = ImageTk.PhotoImage(Image.fromarray(event.frame))
                    self.send_frame(ai2thor_frame)
                    self.action_list.append("MoveBack")
                elif keyboard.is_pressed('left'):
                    event = controller.step(dict(action='MoveLeft'))
                    ai2thor_frame = ImageTk.PhotoImage(Image.fromarray(event.frame))
                    self.send_frame(ai2thor_frame)
                    self.action_list.append("MoveLeft")
                elif keyboard.is_pressed('8'):
                    event = controller.step(dict(action='MoveHandAhead', moveMagnitude=0.1))
                    ai2thor_frame = ImageTk.PhotoImage(Image.fromarray(event.frame))
                    self.send_frame(ai2thor_frame)
                    self.action_list.append("MoveHandAhead")
                elif keyboard.is_pressed('5'):
                    event = controller.step(dict(action='MoveHandBack', moveMagnitude=0.1))
                    ai2thor_frame = ImageTk.PhotoImage(Image.fromarray(event.frame))
                    self.send_frame(ai2thor_frame)
                    self.action_list.append("MoveHandBack")
                elif keyboard.is_pressed('4'):
                    event = controller.step(dict(action='MoveHandLeft', moveMagnitude=0.1))
                    ai2thor_frame = ImageTk.PhotoImage(Image.fromarray(event.frame))
                    self.send_frame(ai2thor_frame)
                    self.action_list.append("MoveHandLeft")
                elif keyboard.is_pressed('6'):
                    event = controller.step(dict(action='MoveHandRight', moveMagnitude=0.1))
                    ai2thor_frame = ImageTk.PhotoImage(Image.fromarray(event.frame))
                    self.send_frame(ai2thor_frame)
                    self.action_list.append("MoveHandRight")
                elif keyboard.is_pressed('7'):
                    event = controller.step(dict(action='MoveHandUp', moveMagnitude=0.1))
                    ai2thor_frame = ImageTk.PhotoImage(Image.fromarray(event.frame))
                    self.send_frame(ai2thor_frame)
                    self.action_list.append("MoveHandUp")
                elif keyboard.is_pressed('9'):
                    event = controller.step(dict(action='MoveHandDown', moveMagnitude=0.1))
                    ai2thor_frame = ImageTk.PhotoImage(Image.fromarray(event.frame))
                    self.send_frame(ai2thor_frame)
                    self.action_list.append("MoveHandDown")
                elif keyboard.is_pressed('1'):
                    anglehandx = anglehandx + 30.0
                    event = controller.step(dict(action='RotateHand', x=anglehandx))
                    ai2thor_frame = ImageTk.PhotoImage(Image.fromarray(event.frame))
                    self.send_frame(ai2thor_frame)
                    self.action_list.append("RotateHandX")
                elif keyboard.is_pressed('2'):
                    anglehandy = anglehandy + 30.0
                    event = controller.step(dict(action='RotateHand', y=anglehandy))
                    ai2thor_frame = ImageTk.PhotoImage(Image.fromarray(event.frame))
                    self.send_frame(ai2thor_frame)
                    self.action_list.append("RotateHandY")
                elif keyboard.is_pressed('3'):
                    anglehandz = anglehandz + 30.0
                    event = controller.step(dict(action='RotateHand', z=anglehandz))
                    ai2thor_frame = ImageTk.PhotoImage(Image.fromarray(event.frame))
                    self.send_frame(ai2thor_frame)
                    self.action_list.append("RotateHandZ")
                elif keyboard.is_pressed('a'):
                    event = controller.step(dict(action='RotateLeft'))
                    # position = event.metadata['agent']['position']
                    # rotation = event.metadata['agent']['rotation']
                    # event = controller.step(
                    #     dict(action='TeleportFull', x=position.get('x'), y=position.get('y'), z=position.get('z'),
                    #          rotation=int(round(rotation.get('y') - 30.0)), horizon=0.0))
                    # time.sleep(.3)
                    # print(rotation)
                    ai2thor_frame = ImageTk.PhotoImage(Image.fromarray(event.frame))
                    self.send_frame(ai2thor_frame)
                    self.action_list.append("RotateLeft")
                elif keyboard.is_pressed('d'):
                    event = controller.step(dict(action='RotateRight'))
                    # position = event.metadata['agent']['position']
                    # rotation = event.metadata['agent']['rotation']
                    # event = controller.step(
                    #     dict(action='TeleportFull', x=position.get('x'), y=position.get('y'), z=position.get('z'),
                    #          rotation=int(round(rotation.get('y') + 30.0)), horizon=0.0))
                    # time.sleep(.3)
                    # print(rotation)
                    ai2thor_frame = ImageTk.PhotoImage(Image.fromarray(event.frame))
                    self.send_frame(ai2thor_frame)
                    self.action_list.append("RotateRight")
                elif keyboard.is_pressed('w'):
                    event = controller.step(dict(action='LookUp'))
                    ai2thor_frame = ImageTk.PhotoImage(Image.fromarray(event.frame))
                    self.send_frame(ai2thor_frame)
                    self.action_list.append("LookUp")
                elif keyboard.is_pressed('s'):
                    event = controller.step(dict(action='LookDown'))
                    ai2thor_frame = ImageTk.PhotoImage(Image.fromarray(event.frame))
                    self.send_frame(ai2thor_frame)
                    self.action_list.append("LookDown")
            elif stage == 'get_instance_obj':
                # Send list of objects in current instance segmentation frame to GUI
                obj_distance = {}
                lowest_dict = {}
                objects = []

                for obj in event.instance_detections2D:
                    objects.append(obj)

                objects = [x for x in objects if not re.search('CounterTop', x)]
                objects = [x for x in objects if not re.search('Shelf', x)]
                objects = [x for x in objects if not re.search('TableTop', x)]

                for obj in event.metadata['objects']:
                    # Remove underscore and characters after underscore
                    # obj_name1 = re.search('^[^_]+', obj_id['name']).group()
                    # if obj_name1 not in objects:
                    obj_distance[obj['objectId']] = obj['distance']

                for i, v in obj_distance.items():
                    if 'CounterTop' in i:
                        lowest_dict[i] = v
                if not len(lowest_dict) == 0:
                    lowest = min(lowest_dict.items(), key=operator.itemgetter(1))[0]
                    objects.append(lowest)
                    lowest_dict.clear()

                # for i, v in obj_distance.items():
                #     if 'BreadSliced' in i:
                #         lowest_dict[i] = v
                # if not len(lowest_dict) == 0:
                #     lowest = min(lowest_dict.items(), key=operator.itemgetter(1))[0]
                #     objects.append(lowest)
                #     lowest_dict.clear()

                # for i, v in obj_distance.items():
                #     if 'TomatoSliced' in i:
                #         lowest_dict[i] = v
                # if not len(lowest_dict) == 0:
                #     lowest = min(lowest_dict.items(), key=operator.itemgetter(1))[0]
                #     objects.append(lowest)
                #     lowest_dict.clear()

                # for i, v in obj_distance.items():
                #     if 'AppleSliced' in i:
                #         lowest_dict[i] = v
                # if not len(lowest_dict) == 0:
                #     lowest = min(lowest_dict.items(), key=operator.itemgetter(1))[0]
                #     objects.append(lowest)
                #     lowest_dict.clear()

                # for i, v in obj_distance.items():
                #     if 'LettuceSliced' in i:
                #         lowest_dict[i] = v
                # if not len(lowest_dict) == 0:
                #     lowest = min(lowest_dict.items(), key=operator.itemgetter(1))[0]
                #     objects.append(lowest)
                #     lowest_dict.clear()

                # for i, v in obj_distance.items():
                #     if 'PotatoSliced' in i:
                #         lowest_dict[i] = v
                # if not len(lowest_dict) == 0:
                #     lowest = min(lowest_dict.items(), key=operator.itemgetter(1))[0]
                #     objects.append(lowest)
                #     lowest_dict.clear()

                for i, v in obj_distance.items():
                    if 'Shelf' in i:
                        lowest_dict[i] = v
                if not len(lowest_dict) == 0:
                    lowest = min(lowest_dict.items(), key=operator.itemgetter(1))[0]
                    objects.append(lowest)
                    lowest_dict.clear()

                for i, v in obj_distance.items():
                    if 'TableTop' in i:
                        lowest_dict[i] = v
                if not len(lowest_dict) == 0:
                    lowest = min(lowest_dict.items(), key=operator.itemgetter(1))[0]
                    objects.append(lowest)
                    lowest_dict.clear()

                self.object_queue.put(objects)
                stage = 'do_input'
            elif stage == 'do_input':
                try:
                    interaction = self.input_queue.get(0)
                    if interaction[0] == 'emphasis':
                        event = controller.step({"action": "EmphasizeObject", "objectId": interaction[1]})
                        # Send frame to GUI
                        ai2thor_frame = ImageTk.PhotoImage(Image.fromarray(event.frame))
                        self.send_frame(ai2thor_frame)
                    elif interaction[0] == 'interaction':
                        event = controller.step({"action": "UnemphasizeAll"})
                        if interaction[1] == 'Break':
                            event = controller.step(dict(action='BreakObject', objectId=interaction[2]))
                            if event.metadata['lastActionSuccess']:
                                self.action_list.append("BreakObject")
                                self.action_list.append(interaction[2])
                        elif interaction[1] == 'Clean':
                            event = controller.step(dict(action='CleanObject', objectId=interaction[2]))
                            if event.metadata['lastActionSuccess']:
                                self.action_list.append("CleanObject")
                                self.action_list.append(interaction[2])
                        elif interaction[1] == 'Close':
                            event = controller.step(dict(action='CloseObject', objectId=interaction[2]))
                            if event.metadata['lastActionSuccess']:
                                self.action_list.append("CloseObject")
                                self.action_list.append(interaction[2])
                        elif interaction[1] == 'Dirty':
                            event = controller.step(dict(action='DirtyObject', objectId=interaction[2]))
                            if event.metadata['lastActionSuccess']:
                                self.action_list.append("DirtyObject")
                                self.action_list.append(interaction[2])
                        elif interaction[1] == 'Drop':
                            event = controller.step(dict(action='DropHandObject'))
                            if event.metadata['lastActionSuccess']:
                                self.action_list.append("DropHandObject")
                        elif interaction[1] == 'Stand':
                            event = controller.step(dict(action='Stand'))
                            if event.metadata['lastActionSuccess']:
                                self.action_list.append("Stand")
                        elif interaction[1] == 'Crouch':
                            event = controller.step(dict(action='Crouch'))
                            if event.metadata['lastActionSuccess']:
                                self.action_list.append("Crouch")
                        elif interaction[1] == 'Empty':
                            event = controller.step(dict(action='EmptyLiquidFromObject', objectId=interaction[2]))
                            if event.metadata['lastActionSuccess']:
                                self.action_list.append("EmptyLiquidFromObject")
                                self.action_list.append(interaction[2])
                        elif interaction[1] == 'Fill':
                            event = controller.step(
                                dict(action='FillObjectWithLiquid', objectId=interaction[2], fillLiquid=interaction[3]))
                            if event.metadata['lastActionSuccess']:
                                self.action_list.append("FillObjectWithLiquid")
                                self.action_list.append(interaction[2])
                                self.action_list.append(interaction[3])
                        elif interaction[1] == 'Open':
                            event = controller.step(dict(action='OpenObject', objectId=interaction[2]))
                            if event.metadata['lastActionSuccess']:
                                self.action_list.append("OpenObject")
                                self.action_list.append(interaction[2])
                        elif interaction[1] == 'Used up':
                            event = controller.step(dict(action='UseUpObject', objectId=interaction[2]))
                            if event.metadata['lastActionSuccess']:
                                self.action_list.append("UseUpObject")
                        elif interaction[1] == 'Pick up':
                            event = controller.step(dict(action='PickupObject', objectId=interaction[2]))
                            if event.metadata['lastActionSuccess']:
                                self.action_list.append("PickupObject")
                                self.action_list.append(interaction[2])
                        elif interaction[1] == 'Pull':
                            event = controller.step(
                                dict(action='PullObject', objectId=interaction[2], moveMagnitude=10.0))
                            if event.metadata['lastActionSuccess']:
                                self.action_list.append("PullObject")
                                self.action_list.append(interaction[2])
                        elif interaction[1] == 'Push':
                            event = controller.step(
                                dict(action='PushObject', objectId=interaction[2], moveMagnitude=10.0))
                            if event.metadata['lastActionSuccess']:
                                self.action_list.append("PushObject")
                                self.action_list.append(interaction[2])
                        elif interaction[1] == 'Put down':
                            event = controller.step(
                                dict(action='PutObject', objectId=interaction[2], receptacleObjectId=interaction[4],
                                     forceAction=True))
                            if event.metadata['lastActionSuccess']:
                                self.action_list.append("PutObject")
                                self.action_list.append(interaction[2])
                                self.action_list.append(interaction[4])
                        elif interaction[1] == 'Slice':
                            event = controller.step(dict(action='SliceObject', objectId=interaction[2]))
                            if event.metadata['lastActionSuccess']:
                                self.action_list.append("SliceObject")
                                self.action_list.append(interaction[2])
                        elif interaction[1] == 'Throw':
                            event = controller.step(dict(action='ThrowObject', moveMagnitude=100.0))
                            if event.metadata['lastActionSuccess']:
                                self.action_list.append("ThrowObject")
                        elif interaction[1] == 'Toggle off':
                            event = controller.step(dict(action='ToggleObjectOff', objectId=interaction[2]))
                            if event.metadata['lastActionSuccess']:
                                self.action_list.append("ToggleObjectOff")
                                self.action_list.append(interaction[2])
                        elif interaction[1] == 'Toggle on':
                            event = controller.step(dict(action='ToggleObjectOn', objectId=interaction[2]))
                            if event.metadata['lastActionSuccess']:
                                self.action_list.append("ToggleObjectOn")
                                self.action_list.append(interaction[2])
                        # Send frame to GUI
                        ai2thor_frame = ImageTk.PhotoImage(Image.fromarray(event.frame))
                        self.send_frame(ai2thor_frame)
                except queue.Empty:
                    pass
            elif stage == 'review':
                with self.frame_queue.mutex:
                    self.frame_queue.queue.clear()

                # use task to set initial config for scene
                controller.reset('FloorPlan' + scene)
                event = controller.step(dict(action='Initialize', gridSize=0.25, renderObjectImage="True"))

                # set initial config for scene
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

                with open('saved-tasks/settings.txt', 'r') as f:
                    settings = f.readlines()
                    settings_list = [x.replace('\n', '') for x in settings]
                if settings_list[0] in config_task_list:
                    scene_config = config_task_list.index(settings_list[0])
                else:
                    scene_config = -1
                f.close()

                if scene_config == -1:
                    ai2thor_frame = ImageTk.PhotoImage(Image.fromarray(event.frame))
                    self.send_frame(ai2thor_frame)
                elif scene_config == 0:
                    for obj in event.metadata['objects']:
                        if obj['objectType'] == 'Plate' or obj['objectType'] == 'Bowl':
                            target_id = obj['objectId']
                            event = controller.step(dict(action='SpecificToggleSpecificState', StateChange='DirtyObject', objectId=target_id))
                    ai2thor_frame = ImageTk.PhotoImage(Image.fromarray(event.frame))
                    self.send_frame(ai2thor_frame)
                elif scene_config == 1:
                    for obj in event.metadata['objects']:
                        if obj['objectType'] == 'Egg':
                            target_id = obj['objectId']
                            event = controller.step(dict(action='SpecificToggleSpecificState', StateChange='BreakObject', objectId=target_id))
                    ai2thor_frame = ImageTk.PhotoImage(Image.fromarray(event.frame))
                    self.send_frame(ai2thor_frame)
                elif scene_config == 2:
                    for obj in event.metadata['objects']:
                        if obj['objectType'] == 'Apple':
                            target_id = obj['objectId']
                            event = controller.step(dict(action='SpecificToggleSpecificState', StateChange='SliceObject', objectId=target_id))
                    ai2thor_frame = ImageTk.PhotoImage(Image.fromarray(event.frame))
                    self.send_frame(ai2thor_frame)
                elif scene_config == 3:
                    for obj in event.metadata['objects']:
                        if obj['objectType'] == 'Cup':
                            target_id = obj['objectId']
                            event = controller.step(dict(action='SpecificToggleSpecificState', StateChange="FillObjectWithLiquid", objectId=target_id, fillLiquid='coffee'))
                    ai2thor_frame = ImageTk.PhotoImage(Image.fromarray(event.frame))
                    self.send_frame(ai2thor_frame)
                elif scene_config == 4:
                    for obj in event.metadata['objects']:
                        if obj['objectType'] == 'Pot':
                            target_id = obj['objectId']
                            event = controller.step(dict(action='SpecificToggleSpecificState', StateChange="FillObjectWithLiquid", objectId=target_id, fillLiquid='water'))
                elif scene_config == 5:
                    for obj in event.metadata['objects']:
                        if obj['objectType'] == 'Laptop':
                            target_id = obj['objectId']
                            event = controller.step(dict(action='SpecificToggleSpecificState', StateChange="CloseObject", objectId=target_id))
                    ai2thor_frame = ImageTk.PhotoImage(Image.fromarray(event.frame))
                    self.send_frame(ai2thor_frame)
                elif scene_config == 6:
                    for obj in event.metadata['objects']:
                        if obj['objectType'] == 'TissueBox':
                            target_id = obj['objectId']
                            event = controller.step(dict(action='SpecificToggleSpecificState', StateChange="UseUpObject", objectId=target_id))
                    ai2thor_frame = ImageTk.PhotoImage(Image.fromarray(event.frame))
                    self.send_frame(ai2thor_frame)
                elif scene_config == 7:
                    for obj in event.metadata['objects']:
                        if obj['objectType'] == 'DeskLamp':
                            target_id = obj['objectId']
                            event = controller.step(dict(action='SpecificToggleSpecificState', StateChange="ToggleObjectOn", objectId=target_id))
                    ai2thor_frame = ImageTk.PhotoImage(Image.fromarray(event.frame))
                    self.send_frame(ai2thor_frame)
                elif scene_config == 8:
                    for obj in event.metadata['objects']:
                        if obj['objectType'] == 'Blinds':
                            target_id = obj['objectId']
                            event = controller.step(dict(action='SpecificToggleSpecificState', StateChange="CloseObject", objectId=target_id))
                    ai2thor_frame = ImageTk.PhotoImage(Image.fromarray(event.frame))
                    self.send_frame(ai2thor_frame)
                elif scene_config == 9:
                    for obj in event.metadata['objects']:
                        if obj['objectType'] == 'Bed':
                            target_id = obj['objectId']
                            event = controller.step(dict(action='SpecificToggleSpecificState', StateChange='DirtyObject', objectId=target_id))
                    ai2thor_frame = ImageTk.PhotoImage(Image.fromarray(event.frame))
                    self.send_frame(ai2thor_frame)
                elif scene_config == 10:
                    for obj in event.metadata['objects']:
                        if obj['objectType'] == 'Blinds':
                            target_id = obj['objectId']
                            event = controller.step(dict(action='SpecificToggleSpecificState', StateChange="OpenObject", objectId=target_id))
                    ai2thor_frame = ImageTk.PhotoImage(Image.fromarray(event.frame))
                    self.send_frame(ai2thor_frame)
                elif scene_config == 11:
                    for obj in event.metadata['objects']:
                        if obj['objectType'] == 'Candle':
                            target_id = obj['objectId']
                            event = controller.step(dict(action='SpecificToggleSpecificState', StateChange="ToggleObjectOn", objectId=target_id))
                    ai2thor_frame = ImageTk.PhotoImage(Image.fromarray(event.frame))
                    self.send_frame(ai2thor_frame)
                elif scene_config == 12:
                    for obj in event.metadata['objects']:
                        if obj['objectType'] == 'ToiletPaper' or obj['objectType'] == 'SoapBottle':
                            target_id = obj['objectId']
                            event = controller.step(dict(action='SpecificToggleSpecificState', StateChange="UseUpObject", objectId=target_id))
                    ai2thor_frame = ImageTk.PhotoImage(Image.fromarray(event.frame))
                    self.send_frame(ai2thor_frame)
                elif scene_config == 13:
                    for obj in event.metadata['objects']:
                        if obj['objectType'] == 'WateringCan':
                            target_id = obj['objectId']
                            event = controller.step(dict(action='SpecificToggleSpecificState', StateChange="FillObjectWithLiquid", objectId=target_id, fillLiquid='water'))
                    ai2thor_frame = ImageTk.PhotoImage(Image.fromarray(event.frame))
                    self.send_frame(ai2thor_frame)
                elif scene_config == 14:
                    for obj in event.metadata['objects']:
                        if obj['objectType'] == 'Mirror':
                            target_id = obj['objectId']
                            event = controller.step(dict(action='SpecificToggleSpecificState', StateChange="DirtyObject", objectId=target_id))
                    ai2thor_frame = ImageTk.PhotoImage(Image.fromarray(event.frame))
                    self.send_frame(ai2thor_frame)
                elif scene_config == 15:
                    for obj in event.metadata['objects']:
                        if obj['objectType'] == 'FloorLamp':
                            target_id = obj['objectId']
                            event = controller.step(dict(action='SpecificToggleSpecificState', StateChange="ToggleObjectOff", objectId=target_id))
                    ai2thor_frame = ImageTk.PhotoImage(Image.fromarray(event.frame))
                    self.send_frame(ai2thor_frame)
                elif scene_config == 16:
                    for obj in event.metadata['objects']:
                        if obj['objectType'] == 'Cloth':
                            target_id = obj['objectId']
                            event = controller.step(dict(action='SpecificToggleSpecificState', StateChange="DirtyObject", objectId=target_id))
                    ai2thor_frame = ImageTk.PhotoImage(Image.fromarray(event.frame))
                    self.send_frame(ai2thor_frame)

                actions = str(self.action_list)
                actions = actions.replace('[', '')
                actions = actions.replace(']', '')
                actions = actions.replace("'", '')
                new_action_list = actions.split(",")
                new_action_list = [word.strip() for word in new_action_list]
                a = 0
                anglehandx = 0.0
                anglehandy = 0.0
                anglehandz = 0.0

                # Send replay action frames to GUI
                with open('saved-tasks/settings.txt', 'r') as f:
                    settings = f.readlines()

                    settings_list = [x.replace('\n', '') for x in settings]
                with open('saved-tasks/user.txt', 'r') as f:
                    user_id = f.readline()
                replaycount=0
                finish=0
                newpath = '/home/user/Desktop/actionet/annotator/recorded_video/' + str(user_id) + '_' + settings_list[
                    0] + '_' + settings_list[1]
                if not os.path.exists(newpath):
                    # os.remove()
                    os.makedirs(newpath)
                for action in new_action_list:
                    # to check for user skipping replay video
                    try:
                        stage = self.stage_queue.get(0)
                        if stage == 'save':
                            with open('saved-tasks/settings.txt', 'r') as f:
                                settings = f.readlines()

                                settings_list = [x.replace('\n', '') for x in settings]
                            with open('saved-tasks/user.txt', 'r') as f:
                                user_id = f.readline()
                                # print(user_id)
                                # print(settings_list[0])
                                # print(settings_list[1])


                            with open("saved-tasks/" + str(user_id) + '/' + settings_list[0] + "_" + settings_list[1], 'w') as f:
                                f.write(str(settings_list))
                                f.write(str(self.action_list))
                            f.close()
                        break
                    except queue.Empty:
                        # check and do action

                        if action == 'PickupObject' or action == 'UseUpObject' or action == 'EmptyLiquidFromObject' or action == 'ToggleObjectOn' or action == 'ToggleObjectOff' or action == 'OpenObject' or action == 'CloseObject' or action == 'SliceObject' or action == 'BreakObject' or action == 'DirtyObject' or action == 'CleanObject':
                            event = controller.step(dict(action=action, objectId=new_action_list[a + 1]))

                        elif action == 'PutObject':
                            event = controller.step(dict(action=action, objectId=new_action_list[a + 1],
                                                         receptacleObjectId=new_action_list[a + 2],forceAction=True))

                        elif action == 'ThrowObject' or action == 'PushObject' or action == 'PullObject':
                            event = controller.step(dict(action=action, moveMagnitude=150.0))

                        elif action == 'FillObjectWithLiquid':
                            event = controller.step(
                                dict(action=action, objectId=new_action_list[a + 1], fillLiquid=new_action_list[a + 2]))

                        elif action=='Stand':
                            event = controller.step(dict(action='Stand'))

                        elif action=='Crouch':
                            event = controller.step(dict(action='Crouch'))

                        elif action=='DropHandObject':
                            event = controller.step(dict(action='DropHandObject'))

                        elif action == 'RotateHandX':
                            anglehandx = anglehandx + 30.0
                            event = controller.step(dict(action='RotateHand', x=anglehandx))

                        elif action == 'RotateHandY':
                            anglehandy = anglehandy + 30.0
                            event = controller.step(dict(action='RotateHand', y=anglehandy))

                        elif action == 'RotateHandZ':
                            anglehandz = anglehandz + 30.0
                            event = controller.step(dict(action='RotateHand', z=anglehandz))

                        elif action == 'MoveHandAhead' or action == 'MoveHandBack' or action == 'MoveHandLeft' or action == 'MoveHandRight' or action == 'MoveHandUp' or action == 'MoveHandDown':
                            event = controller.step(dict(action=action, moveMagnitude=0.1))

                        elif action == 'MoveRight' or action == 'MoveAhead' or action == 'MoveLeft' or action == 'MoveBack' or action == 'RotateLeft' or action == 'RotateRight' or action == 'LookUp' or action == 'LookDown':
                            event = controller.step(dict(action=action))

                        cv2.imwrite('/home/user/Desktop/actionet/annotator/recorded_video/' + str(user_id) + '_' + settings_list[0] + '_' + settings_list[1]+'/'+ str(replaycount) + '.jpg',event.cv2img)
                        replaycount +=1
                        a += 1

                        ai2thor_frame = ImageTk.PhotoImage(Image.fromarray(event.frame))
                        self.send_frame(ai2thor_frame)



    def send_frame(self, frame):
        """Send frame to the frame_queue."""
        self.frame_queue.put(frame)

    def send_current_objects(self, current_objects):
        """Send all object choices to the object_queue."""
        self.object_queue.put(current_objects)


if __name__ == "__main__":
    root = tk.Tk()
    root.wm_geometry("1200x1200")
    time1 = ''
    # Instantiate GUI
    gui = Gui(root)
    root.mainloop()
