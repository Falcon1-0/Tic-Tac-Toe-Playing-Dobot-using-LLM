import Grid as g
import pydobot
import time
import XNO as x
import sampleFile as s
import userMoveDetection as u

device = pydobot.Dobot(port="COM6", verbose=False)

# --------------------------------
# 3️⃣ Set speed and go home
# --------------------------------
device.speed(100, 100)  # (velocity, acceleration)
device.move_to(180, 45, 80, 0,wait=False)
time.sleep(2)

g.draw_tictactoe_grid(device, 200, 0, 20, 0, 20)
device.move_to(180, 45, 80, 0,wait=False)
time.sleep(2)

print("1. Human Plays first")
print("2. Ai plays first")
first_play = int(input("Enter your choice: "))
if first_play == 1:
    symbol = u.detect_player_symbol()
    print(symbol)
    s.main(device,symbol)
elif first_play == 2:
    s.main(device,"X")

#x.draw_X(device, 215, 15)
#x.draw_O(device, 245, 15)

#device.go_home()
device.close()
