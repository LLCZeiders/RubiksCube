'''
Solves rubik's cube by having user take picture of each face of the cube.
The program then takes each side and determines the colors and order, and returns relative position of each square.

Produces relative notation string and passes it through kociemba module/alogrithm to retrieve the solution to the Rubik's cube.
'''
import cv2
import kociemba
import numpy as np


def get_colors(pic):
    # looks at cube face and detects present colors, return dictionary of colors/coordinates
    colors = {
        "red": ([168, 255, 62], [179, 255, 130]),
        "yellow": ([19, 39, 143], [67, 141, 255]),
        "orange": ([0, 136, 111], [13, 236, 178]),  # ranges will need to be adjusted depending on lighting in the room
        "white": ([113, 33, 206], [118, 68, 227]),
        "green": ([69, 81, 27], [91, 156, 233]),
        "blue": ([105, 245, 105], [120, 255, 255])
    }
    
    color_list = {
        'yellow': [],
        'red': [],
        'blue': [],
        'green': [],
        'white': [],
        'orange': [],
    }

    # cycles through color ranges, finding every matching color and its coordinates within the picture
    hsvsquare = cv2.cvtColor(pic, cv2.COLOR_BGR2HSV)
    for color, (lower, upper) in colors.items():  
        mask = cv2.inRange(hsvsquare, np.array(lower, dtype=np.uint8), np.array(upper, dtype=np.uint8))
        cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for c in cnts:
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.04 * peri, True)
            area = cv2.contourArea(c)
            if area > 500:
                x, y, w, h = cv2.boundingRect(approx)
                color_list[color].append((x+w//2, y+h//2))  # gets center of detected color
    return color_list


def order_colors(c_list):
    # orders the colors from get_color function from left-to-right, and top-to-bottom
    color_names = []
    for _ in range(3):
        coords = []

        for color in c_list.keys():  # populates coords to be sorted through
            if color:
                for coord in c_list[color]:
                    coords.append((color, coord[0], coord[1]))

        def sort_by_y(e):
            return e[2]

        def sort_by_x(e):
            return e[1]

        # Sorts by y coordinate, then getting the lowest 3 (the top 3 squares).
        coords.sort(key=sort_by_y)
        coords = coords[:3]
        coords.sort(key=sort_by_x)  # then sorts those 3 by x coordinate to determine left to right order

        # deletes 3 (now ordered) squares and reruns the code, now missing the top 3
        # so it automatically sorts from top to bottom
        for item in coords:
            color_names.append(item[0])
            c_list[item[0]].pop(c_list[item[0]].index((item[1], item[2])))

    if len(color_names) == 9:
        return color_names
    return False  # retakes image if colors not collected properly !!!This does not work properly and just prints "False" for some reason


def get_orientation(color_list):
    ''' 
    returns relative notation
    U R F D L B
    U - up
    R - right
    F - front
    D - down
    L - left
    B - back
    '''
    directions = {
        'U': '',
        'R': '',
        'F': '',
        'D': '',
        'L': '',
        'B': ''
    }
    i = 0
    for item in directions:
        directions[item] = color_list[i][4]
        i += 1

    notation = ''

    for face in range(6):
        for square in range(9):
            for i in directions:
                if directions[i] == color_list[face][square]:
                    notation += i

    return notation


def main():
    cap = cv2.VideoCapture(0)
    side = []
    color_list = []
    notation = ''

    while True:
        _, frame = cap.read()
        cv2.imshow('monitor', frame)

        if side:
            colornames = get_colors(side[0])
            if colornames:
                ordered = order_colors(colornames)
                print(ordered)
                color_list.append(ordered)
                side = []
            else:
                print('take pic again')  #this does not work properly
                side = []
                continue

        if len(color_list) == 6:
            notation = get_orientation(color_list)
            color_list = []
            break

        k = cv2.waitKey(1)
        if k & 0xff == ord('q'):
            break
        if k & 0xff == ord(' '):  # press space to take still image of side
            side.append(frame)
            print("pic taken")
    if notation:
        print(f"Answer: {kociemba.solve(notation)}")
    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
