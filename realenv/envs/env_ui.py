import pygame
from pygame import surfarray
from pygame.surfarray import pixels3d
import time
import numpy as np
import cv2
import os
from datetime import datetime
from PIL import Image
import scipy.misc
from realenv.core.render.profiler import Profiler
from realenv import configs

class SimpleUI():
    '''Static UI'''
    RECORD_ROOT = "/home/zhiyang/Desktop/realenv/recordings"

    def __init__(self, width, height):
        self.width  = width
        self.height = height
        self.screen = pygame.display.set_mode([width, height], 0, 32)
        self.screen_arr = np.zeros([width, height, 3])
        self.screen_arr.fill(255)
        self.is_recording = False

    def add_image(self, img, x, y):
        #self.screen.blit(img, (x, y))
        self.screen_arr[x: x + img.shape[0], y:y + img.shape[1], :] = img

    def clear(self):
        self.screen_arr.fill(255)
        self.refresh()

    def refresh(self):
        if configs.ENABLE_UI_RECORDING:
            cmd=cv2.waitKey(5)%256
            if cmd == ord('r'):
                self.start_record()
            if cmd == ord('q'):
                self.end_record()

            img = np.uint8(self.screen_arr)
            cv2.imshow("Recording", img)
            if self.is_recording:
                self.curr_output.write(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        #with Profiler("Refreshing"):
        pygame.display.flip()
        surfarray.blit_array(self.screen, np.swapaxes(self.screen_arr, 0, 1))
        #surf = pygame.surfarray.make_surface(self.screen_arr)
        #self.screen.blit(surf, (0, 0))
        #pygame.display.update()


    def start_record(self):
        print("start recording")
        if self.is_recording:
            return    # prevent double enter
        fourcc = cv2.VideoWriter_fourcc(*'MJPG') # 'XVID' smaller
        file_keyword = datetime.now()
        filename = 'record-{}.avi'.format(file_keyword)
        filepath = os.path.join(self.RECORD_ROOT, filename)

        foldername = 'record-{}'.format(file_keyword)
        folderpath = os.path.join(self.RECORD_ROOT, foldername)

        #os.mkdir(folderpath)
        self.curr_output = cv2.VideoWriter(filepath, fourcc, 22.0, self.UI_DIM)

        self.is_recording = True

    def make_video(self):
        return

    def end_record(self):
        print("end recording")
        self.curr_output.release()
        self.is_recording = False
        return


class SixViewUI(SimpleUI):
    '''UI with all modalities, default resolution
    RGB:       512x512, (top left)
    Map:       256x256, (top right)
    Physics:   256x256, (center right)
    Depth:     256x256, (bottom left)
    Semantics: 256x256, (bottom right)
    Normal:    256x256  (bottom right)
    '''
    UI_DIM    = (768, 768)
    POS_RGB   = (0, 0)
    POS_PHYSICS = (512, 256)
    POS_MAP   = (512, 0)
    POS_DEPTH = (0, 512)
    POS_SEM   = (512, 512)
    POS_SURF  = (256, 512)
    def __init__(self):
        SimpleUI.__init__(self, 768, 768)
        self.add_all_images()


    def add_all_images(self):
        img_rgb = np.zeros((512, 512, 3))
        img_map = np.zeros((256, 256, 3))
        img_physics = np.zeros((256, 256, 3))
        img_sem = np.zeros((256, 256, 3))
        img_surf = np.zeros((256, 256, 3))
        img_depth = np.zeros((256, 256, 3))

        img_rgb.fill(100)
        img_map.fill(120)
        img_physics.fill(140)
        img_depth.fill(120)
        img_sem.fill(180)
        img_surf.fill(200)

        self.add_image(img_rgb, self.POS_RGB[0], self.POS_RGB[1])
        self.add_image(img_sem, self.POS_SEM[0], self.POS_SEM[1])
        self.add_image(img_depth, self.POS_DEPTH[0], self.POS_DEPTH[1])
        self.add_image(img_physics, self.POS_PHYSICS[0], self.POS_PHYSICS[1])
        self.add_image(img_surf, self.POS_SURF[0], self.POS_SURF[1])
        self.add_image(img_map, self.POS_MAP[0], self.POS_MAP[1])

    def update_rgb(self, rgb):
        #rgb = pygame.transform.rotate(rgb, 90)
        self.add_image(rgb, self.POS_RGB[1], self.POS_RGB[0])

    def update_sem(self, sem):
        #sem = pygame.transform.rotate(sem, 90)
        self.add_image(sem, self.POS_SEM[1], self.POS_SEM[0])

    def update_physics(self, physics):
        #physics = pygame.transform.rotate(physics, 90)
        self.add_image(physics, self.POS_PHYSICS[1], self.POS_PHYSICS[0])

    def update_depth(self, depth):
        #depth = pygame.transform.rotate(depth, 90)
        self.add_image(depth, self.POS_DEPTH[1], self.POS_DEPTH[0])

    def update_normal(self, surf):
        self.add_image(surf, self.POS_SURF[1], self.POS_SURF[0])

    def update_map(self, map_img):
        self.add_image(map_img, self.POS_MAP[1], self.POS_MAP[0])


class FourViewUI(SimpleUI):
    '''UI with four modalities, default resolution
    Physics:   256x256, (top left)
    Depth:     256x256, (top right)
    RGB:       256x256, (bottom left)
    Unfilled:  256x256  (bottom right)
    '''
    UI_DIM    = (512, 512)
    POS_RGB   = (0, 256)
    POS_PHYSICS = (0, 0)
    POS_DEPTH   = (256, 0)
    POS_UNFILL = (256, 256)
    def __init__(self):
        SimpleUI.__init__(self, 512, 512)
        self.add_all_images()

    def add_all_images(self):
        img_rgb = np.zeros((256, 256, 3))
        img_physics = np.zeros((256, 256, 3))
        img_depth = np.zeros((256, 256, 3))
        img_unfill = np.zeros((256, 256, 3))

        img_rgb.fill(100)
        img_depth.fill(120)
        img_physics.fill(140)
        img_unfill.fill(180)

        self.add_image(img_rgb, self.POS_RGB[0], self.POS_RGB[1])
        self.add_image(img_depth, self.POS_DEPTH[0], self.POS_DEPTH[1])
        self.add_image(img_physics, self.POS_PHYSICS[0], self.POS_PHYSICS[1])
        self.add_image(img_unfill, self.POS_UNFILL[0], self.POS_UNFILL[1])

    def update_rgb(self, rgb):
        self.add_image(rgb, self.POS_RGB[1], self.POS_RGB[0])

    def update_unfilled(self, unfill):
        self.add_image(unfill, self.POS_UNFILL[1], self.POS_UNFILL[0])

    def update_physics(self, physics):
        self.add_image(physics, self.POS_PHYSICS[1], self.POS_PHYSICS[0])

    def update_depth(self, depth):
        #depth = pygame.transform.rotate(depth, 90)
        self.add_image(depth, self.POS_DEPTH[1], self.POS_DEPTH[0])

class TwoViewUI(SimpleUI):
    '''UI with four modalities, default resolution
    Physics:   256x256,
    RGB:       256x256,
    '''
    UI_DIM    = (512, 256)
    POS_RGB   = (256, 0)
    POS_PHYSICS = (0, 0)
    def __init__(self):
        SimpleUI.__init__(self, 512, 256)
        self.add_all_images()

    def add_all_images(self):
        img_rgb = np.zeros((256, 256, 3))
        img_physics = np.zeros((256, 256, 3))

        img_rgb.fill(100)
        img_physics.fill(140)

        self.add_image(img_rgb, self.POS_RGB[0], self.POS_RGB[1])
        self.add_image(img_physics, self.POS_PHYSICS[0], self.POS_PHYSICS[1])

    def update_rgb(self, rgb):
        self.add_image(rgb, self.POS_RGB[1], self.POS_RGB[0])

    def update_physics(self, physics):
        self.add_image(physics, self.POS_PHYSICS[1], self.POS_PHYSICS[0])


def main6():
    UI = SimpleUI(768, 768)

    ## Center left top
    grey_1 = np.zeros((512, 512, 3))
    grey_1.fill(100)

    ## Right top
    grey_2 = np.zeros((256, 256, 3))
    grey_2.fill(120)

    ## Right mid
    grey_3 = np.zeros((256, 256, 3))
    grey_3.fill(140)

    ## Bottom left
    grey_4 = np.zeros((256, 256, 3))
    grey_4.fill(120)

    ## Bottom mid
    grey_5 = np.zeros((256, 256, 3))
    grey_5.fill(180)

    ## Bottom right
    grey_6 = np.zeros((256, 256, 3))
    grey_6.fill(200)


    UI = SixViewUI()
    rgb = np.zeros((512, 512, 3))
    rgb.fill(0)

    while True:
        UI.refresh()
        UI.update_rgb(rgb)
        rgb += 20
        time.sleep(0.2)
        #screen_arr = 255 - screen_arr


def main4():
    UI = SimpleUI(256, 256)

    ## Center left top
    grey_1 = np.zeros((256, 256, 3))
    grey_1.fill(100)

    ## Right top
    grey_2 = np.zeros((256, 256, 3))
    grey_2.fill(120)

    ## Right mid
    grey_3 = np.zeros((256, 256, 3))
    grey_3.fill(140)

    ## Bottom left
    grey_4 = np.zeros((256, 256, 3))
    grey_4.fill(160)

    UI = FourViewUI()
    rgb = np.zeros((256, 256, 3))
    rgb.fill(0)

    UI.update_physics(grey_1)
    UI.update_depth(grey_2)
    UI.update_rgb(grey_3)
    UI.update_unfilled(grey_4)

    while True:
        UI.refresh()
        UI.update_rgb(rgb)
        rgb += 20
        time.sleep(0.2)
        #screen_arr = 255 - screen_arr

def main2():
    ## Center left top
    grey_1 = np.zeros((256, 256, 3))
    grey_1.fill(100)

    ## Right top
    grey_2 = np.zeros((256, 256, 3))
    grey_2.fill(120)

    UI = TwoViewUI()
    rgb = np.zeros((256, 256, 3))
    rgb.fill(0)

    UI.update_physics(grey_1)
    UI.update_rgb(grey_2)

    while True:
        UI.refresh()
        UI.update_rgb(rgb)
        rgb += 20
        time.sleep(0.2)
        #screen_arr = 255 - screen_arr

if __name__ == "__main__":
    main6()
    #main2()
    #main4()