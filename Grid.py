import time
def draw_tictactoe_grid(device, origin_x, origin_y, grid_size, pen_down_z, pen_up_z, line_delay=0.05):

    x = origin_x
    y = origin_y
    z = pen_down_z
    z1 = pen_up_z
    
    device.speed(100, 100)
    device.move_to(x, y, z1, 0, wait=False)
    device.move_to(x, y, z, 0, wait=False)
    device.move_to(x, y+90, z, 0, wait=False)
    device.move_to(x+90, y+90, z, 0, wait=False)
    device.move_to(x+90, y, z, 0, wait=False)
    device.move_to(x, y, z, 0, wait=False)

    device.move_to(x, y, z1, 0, wait=False)
    device.move_to(x, y+30, z1, 0, wait=False)
    device.move_to(x, y+30, z, 0, wait=False)
    device.move_to(x+90, y+30, z, 0, wait=False)

    device.move_to(x+90, y+30, z1, 0, wait=False)
    device.move_to(x+90, y+60, z1, 0, wait=False)
    device.move_to(x+90, y+60, z, 0, wait=False)
    device.move_to(x, y+60, z, 0, wait=False)

    device.move_to(x, y+60, z1, 0, wait=False)
    device.move_to(x+30, y, z1, 0, wait=False)
    device.move_to(x+30, y, z, 0, wait=False)
    device.move_to(x+30, y+90, z, 0, wait=False)

    device.move_to(x+30, y+90, z1, 0, wait=False)
    device.move_to(x+60, y+90, z1, 0, wait=False)
    device.move_to(x+60, y+90, z, 0, wait=False)
    device.move_to(x+60, y, z, 0, wait=False)


    device.move_to(x+60, y, z1, 0, wait=False)
    device.move_to(x, y, z, 0, wait=False)
    time.sleep(line_delay)
    
    print("✅ Turbo grid completed!")
