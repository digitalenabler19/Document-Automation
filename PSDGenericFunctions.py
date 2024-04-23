import os
import numpy as np
import traceback
import random
import logging
import datetime
import json
import copy
import cv2

def create_directory_if_not_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Directory '{directory}' created successfully.")
    else:
        print(f"Directory '{directory}' already exists.")

def logConfig(path):
#os.chdir("../../../ProgramData/AA_Python_Execution_Logs")
    if path != "":
        os.chdir(path)
    currDate = str(datetime.date.today())
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s')
    file_handler = logging.FileHandler(currDate+".log")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger

def shake_image(filepath, docJSONPath, min_pixelsToMove_X,max_pixelsToMove_X, min_pixelsToMove_Y,max_pixelsToMove_Y,sampleCount):
      logger = logConfig('')
      with open(docJSONPath, 'r') as file:
            data = json.load(file)
      #logging.info(f"FilePath: {filepath}, min_pixelsToMove:{min_pixelsToMove_X},max_pixelsToMove:{max_pixelsToMove_X} ,Y-Pixels:{ min_pixelsToMove_Y,max_pixelsToMove_Y}sampleCount:{sampleCount}")
      count = 0
      keyvals = data['engineData']['docDetectResult']['featureObjects']

      # Sort the list based on two number attributes
      sorted_list = sorted(keyvals, key=lambda keyval: (keyval['geometry']['y1'], keyval['geometry']['x1']))
      sorted_list_copy = sorted_list

      sorted_list_orig = list(filter(lambda thiskeyval: thiskeyval['text'] != "", sorted_list))
      sorted_list_copy = copy.deepcopy(sorted_list_orig)

      width = data['engineData']['imagePreprocessingResult']['pages'][0]['width']
      height = data['engineData']['imagePreprocessingResult']['pages'][0]['height']
      logging.info(f"Length of feature objects list: {len(sorted_list)}")
      image_orig = cv2.imread(filepath)
      while count < sampleCount:
            try:
                  pixelsToMove = random.randint(min_pixelsToMove_X,max_pixelsToMove_X)
                  pixelsToMove_Y = random.randint(min_pixelsToMove_Y, max_pixelsToMove_Y)

                  sorted_list = copy.deepcopy(sorted_list_orig)
                  image = copy.deepcopy(image_orig)
                  file_name_save='X_' +str(pixelsToMove) +'_Y_'+str(pixelsToMove_Y)+'_count'+str(count)+'_'+str(random.randint(1, 1000)) + '_' + filepath
                  logging.info(f"-------------------------New sample document getting created:{count} , {file_name_save}----")
                  logging.info( f"pixelsToMove-X:{pixelsToMove},pixelsToMove_Y:{pixelsToMove_Y}")
                  # KEY VALUE
                  index = 0  # tweak to avoid documnet title or company name
                  while index < len(sorted_list):
                        print('count,index,sorted_list ', count, index, len(sorted_list))
                        try:
                              keyval = sorted_list[index]
                              logging.info(f"index:{index}, keyval: {keyval['blockType']}, text:{keyval['text']}")

                              # Crop the text region (invoice number)
                              x_min, y_min, x_max, y_max = (
                                    keyval['geometry']['x1'], keyval['geometry']['y1'], keyval['geometry']['x2'],
                                    keyval['geometry']['y2'])
                              cropped_text_region = copy.deepcopy(image[y_min:y_max, x_min:x_max])
                              logging.info(f"dimensions of block before movement: {y_min},{y_max},{x_min},{x_max}")
                              # find the maximum movement possible

                              # find all keyval blocks in X-Axis which starts in between the row of currently selected block or all keyval blocks that ends more than the current block start


                              #1. Any field that has bounding box Y1 coordinate overlapping with the field considered for movement
                              #2. Any field that has bounding box Y2 coordinate overlapping with the field considered for movement
                              #3. Any field that has bounding box Y1 coordinate before the start of the field considered for movement and Y2 after the end of the field considered for movement
                              srchRes = list(filter(lambda thiskeyval: (thiskeyval['id'] != keyval['id']) and (thiskeyval['geometry']['x1'] < x_min) and ((y_max >= thiskeyval['geometry']['y1'] >= y_min) or (y_max >= thiskeyval['geometry']['y2'] >= y_min) or (thiskeyval['geometry']['y1'] <= y_min and thiskeyval['geometry']['y2'] >= y_min) ),sorted_list))
                              #srchRes = list(map(findXDelta, srchRes))
                              #srchRes_sorted = sorted(srchRes, key=lambda keyval: (keyval['geometry']['y1']), reverse=False)
                              srchRes_sorted = sorted(srchRes, key=lambda keyval: (keyval['geometry']['x2']), reverse=True)
                              # Calculate the new coordinates for the cropped region (move to the left by 20 pixels)
                              new_x_min = x_min - int(pixelsToMove)
                              if new_x_min < 0:
                                    new_x_min = 10
                              # new_x_max = x_max - int(pixelsToMove)
                              new_x_max = new_x_min + (x_max - x_min)


                              #sorted_list_X = sorted(srchRes, key=lambda keyval: (keyval['x_delta']), reverse=False)
                              sorted_list_X = srchRes_sorted
                              if len(sorted_list_X) > 0:
                                    if (x_min - sorted_list_X[0]['geometry']['x2'] ) > 5:
                                          print("block considered for X-axis", sorted_list_X[0])
                                          logging.info(f"block considered for X-axis: {sorted_list_X[0]['blockType']}, text:{sorted_list_X[0]['text']}, geometry:{sorted_list_X[0]['geometry']}")
                                          new_x_min = sorted_list_X[0]['geometry']['x2'] + 5
                                          # new_x_min_temp = sorted_list_X[0]['geometry']['x2'] + 5
                                          # if new_x_min > new_x_min_temp:
                                          #       new_x_min = new_x_min_temp

                                          new_x_max = new_x_min + x_max - x_min

                              # Fill the original region with a suitable background color (white in this example)
                              #background_color = (0, 0, 255)  # red color
                              background_color = (255, 255, 255)  # White color
                              x_min_start = x_max - int(pixelsToMove)

                              # Find all blocks in Y Aixs
                              srchRes_Y = list(filter(lambda thiskeyval: (thiskeyval['id'] != keyval['id']) and (thiskeyval['geometry']['y2'] < y_min) and (
                                            (new_x_max >= thiskeyval['geometry']['x1'] >= new_x_min) or (
                                                  new_x_max >= thiskeyval['geometry']['x2'] >= new_x_min) or (
                                                          thiskeyval['geometry']['x1'] < new_x_min and
                                                          thiskeyval['geometry']['x2'] > new_x_min)), sorted_list))

                              for item in srchRes_Y:
                                    item['y_delta'] = y_min - item['geometry']['y2']
                              srchRes_Y = list(filter(lambda thiskeyval: thiskeyval['y_delta'] >= 0, srchRes_Y))
                              # now loop through above list and find out the nearest block in Y-Axis that won't
                              # block the movement of the current block in Y-Axis
                              #sorted_list_Y = sorted(srchRes_Y, key=lambda keyval: (keyval['y_delta']), reverse=False)
                              new_y_min = y_min -int(pixelsToMove_Y)

                              if new_y_min < 0:
                                    new_y_min = y_min
                              sorted_list_Y = sorted(srchRes_Y, key=lambda keyval: (keyval['geometry']['y2']), reverse=True)
                              if len(sorted_list_Y) > 0:
                                    if (y_min - sorted_list_Y[0]['geometry']['y2'] ) > 2:
                                          print("block considered for Y-axis", sorted_list_Y[0])
                                          logging.info(f"block considered for Y-axis: {sorted_list_Y[0]['blockType']}, text:{sorted_list_Y[0]['text']}")
                                          new_y_min = sorted_list_Y[0]['geometry']['y2'] + 10
                                          # if new_y_min_temp < new_y_min:
                                          #       new_y_min = new_y_min_temp
                              else:
                                    new_y_min = 20
                              new_y_max = new_y_min + (y_max - y_min)

                              #erase existing values after moving using white background color
                              if new_x_max <= x_min:
                                    image[y_min:y_max, x_min:x_max] = background_color
                              elif new_x_min != x_min:# block has move din X-Direction
                                    image[y_min:y_max, new_x_max:x_max] = background_color
                                    logging.info(f"dimensions of eraser in X-Direction: {y_min,y_max, new_x_max,x_max}")
                              if new_y_max <= y_min:
                                    image[y_min:y_max, x_min:x_max] = background_color
                              elif new_y_min != y_min:  # block has move din Y-Direction
                                    image[new_y_max:y_max, x_min:x_max] = background_color
                                    logging.info(f"dimensions of eraser in Y-Direction: {new_y_max, y_max, x_min, x_max}")
                              #image[y_min:y_max, x_min:x_max] = background_color
                              image[new_y_min:new_y_max, new_x_min:new_x_max] = cropped_text_region
                              logging.info(f"dimensions of block after movement: {new_y_min},{new_y_max},{new_x_min},{new_x_max}")
                              # Save or display the modified image
                              orange = (0, 165, 255)

                              # image = cv2.rectangle(image, (x_min_start,y_min), (x_max,y_max), orange, 2)
                              # Remove any others blocks contained inside the current block considered for movement
                              sorted_list = list(filter(
                                    lambda thiskeyval: (thiskeyval['id'] == keyval['id']) or (thiskeyval['geometry']['y1'] < y_min) or (
                                            thiskeyval['geometry']['y2'] > y_max) or (thiskeyval['geometry']['x1'] < x_min) or (
                                                               thiskeyval['geometry']['x2'] > x_max),
                                    sorted_list))  # to search for blocks containing relationship
                              sorted_list_1 = list(filter(lambda thiskeyval: keyval['id'] == '1B1BABC3-9874-48D5-B544-CFAC1C9FA6B3',
                                                          sorted_list))  # to search for blocks containing relationship
                              keyval['geometry']['x1'] = new_x_min
                              keyval['geometry']['y1'] = new_y_min
                              keyval['geometry']['x2'] = new_x_max
                              keyval['geometry']['y2'] = new_y_max
                              #index = index + 112
                              index = index + 1

                        except Exception as innerException:
                              print("EXCEPTION FOUND")
                              # Get the current line number where the exception occurred
                              line_number = traceback.extract_tb(innerException.__traceback__)[-1].lineno
                              # Get the error message
                              error_message = str(innerException)
                              print(line_number, error_message)
                              logging.error(f"line_number: {line_number}, error_message:{error_message}")
                              print('BLOCK CONSIDERED FOR MOVEMENT')
                              print(keyval)
                              print('new coords', new_y_min, new_y_max, new_x_min, new_x_max)
                              print('pixelsToMove:', pixelsToMove)
                              index = index + 1
                              break
                  cv2.imwrite(file_name_save, image)
            except Exception as e:

                line_number_1 = traceback.extract_tb(innerException.__traceback__)[-1].lineno
                # Get the error message
                error_message_1 = str(innerException)
                print("Error Encountered in outer loop", count)
                logging.error("Error Encountered in outer loop", count)
                logging.error(f"line_number: {line_number_1}, error_message:{error_message_1}")
                break
            count = count + 1






