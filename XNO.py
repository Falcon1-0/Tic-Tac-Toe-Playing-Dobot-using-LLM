import time
import math

# ---------------------------------------------------
# 2️⃣ Helper motion functions
# ---------------------------------------------------
PEN_DOWN_Z = 0
PEN_UP_Z = 20

def pen_down(device):
    pose = device.pose()
    device.move_to(pose[0], pose[1], PEN_DOWN_Z, pose[3])

def pen_up(device):
    pose = device.pose()
    device.move_to(pose[0], pose[1], PEN_UP_Z, pose[3])

# ---------------------------------------------------
# 3️⃣ Function to draw an X
# ---------------------------------------------------
def draw_X(device, center_x, center_y, size=25):
    """
    Draws an 'X' centered at (center_x, center_y)
    size: half the distance from center to the end of each line.
    """
    half = size / 2
    print(f"✖ Drawing X at ({center_x}, {center_y})")

    # Diagonal 1: top-left to bottom-right
    x1, y1 = center_x - half, center_y - half
    x2, y2 = center_x + half, center_y + half
    
    device.move_to(x1,y1,PEN_UP_Z,0,wait=False)
    device.move_to(x1,y1,PEN_DOWN_Z,0,wait=False)
    device.move_to(x2,y2,PEN_DOWN_Z,0, wait=False)
    device.move_to(x2,y2,PEN_UP_Z,0, wait=False)
    time.sleep(0.5)

    # Diagonal 2: bottom-left to top-right
    x3, y3 = center_x - half, center_y + half
    x4, y4 = center_x + half, center_y - half
    device.move_to(x3,y3,PEN_UP_Z,0,wait=False)
    device.move_to(x3,y3,PEN_DOWN_Z,0,wait=False)
    device.move_to(x4,y4,PEN_DOWN_Z,0, wait=False)
    device.move_to(x4,y4,PEN_UP_Z,0, wait=False)
    time.sleep(0.5)
    device.move_to(180, 45, 80, 0,wait=False)

# ---------------------------------------------------
# 4️⃣ Function to draw an O (circle)
# ---------------------------------------------------
def draw_O(device, center_x, center_y, radius=12.5, segments=36):
    """
    Draws a circular 'O' centered at (center_x, center_y)
    radius: circle radius in mm
    segments: how many small line segments form the circle
    """
    print(f"⭘ Drawing O at ({center_x}, {center_y})")

    # Generate circle points
    device.speed(150, 150)
    points = []
    for i in range(segments + 1):
        angle = 2 * math.pi * i / segments
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        points.append((x, y))

    device.move_to(points[0][0], points[0][1], PEN_UP_Z, 0)
    for (x, y) in points[0:]:
        device.move_to(x, y, PEN_DOWN_Z, 0)
    device.move_to(points[0][0], points[0][1], PEN_DOWN_Z, 0)
    pen_up(device)
    device.move_to(180, 45, 80, 0,wait=False)

