import gym
import sys, select, termios, tty
from mountain_car import MountainCarEnv

moveBindings = {
        '1': 0,
        '2': 1,
        '3': 2
}


settings = termios.tcgetattr(sys.stdin)

def getKey():
    tty.setraw(sys.stdin.fileno())
    rlist, _, _ = select.select([sys.stdin], [], [])
    if rlist:
        key = sys.stdin.read(1)
    else:
        key = ''

    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key

env = MountainCarEnv()#gym.make('MountainCar-v0')
env.reset()

while True:
    env.render()

    key = getKey()
    if key == 'x':
        exit()
    elif key == 'r': # repeat this game
        ob = env.reset()
        print 'Reset:', ob
        continue

    # Possible actions are: MoveLeft, MoveRight, MoveAhead, MoveBack, LookUp, LookDown, RotateRight, RotateLeft
    if key not in moveBindings:
        print 'Invalid action.'
        continue

    print('Action: ' + key)

    # Take action
    ob, reward, done, _ = env.step(moveBindings[key])

    print 'State:', ob, 'Reward:', reward, 'Done:', done
        
