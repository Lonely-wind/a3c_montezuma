import sys, select, termios, tty
from toy_Montezuma import *

moveBindings = {
        'w': UP,
        's': DOWN,
        'a': LEFT,
        'd': RIGHT,
        ' ': JUMP,
        'q': JUMP_LEFT,
        'e': JUMP_RIGHT
}

gameStatus = {
    1: 'Win',
    0: 'Normal',
    -1: 'Fail'
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

env = MontezumaWorld()
scenario = env.sample_scenario()
state = scenario.init()


while True:
    state.visualize()

    key = getKey()
    if key == 'x':
        exit()
    elif key == 'n': # new game
        scenario = env.sample_scenario()
        state = scenario.init()
        continue
    elif key == 'r': # repeat this game
        state = scenario.init()
        continue

    #print 'The input is', key


    # Possible actions are: MoveLeft, MoveRight, MoveAhead, MoveBack, LookUp, LookDown, RotateRight, RotateLeft
    if key not in moveBindings:
        print 'Invalid action.'
        continue

    print('Action: ' + key)

    # Take action
    flag, action_success, reward, state = state.step(moveBindings[key])

    # True/False whether the last action was successful.  Actions will fail if you attempt to move into a wall or LookUp/Down beyond the allowed range.
    str1 = 'Action success: ' + str(action_success)

    # target_found() returns True/False if the target has been found
    str2 = 'Game status: ' + str(gameStatus[flag])

    print str1 + '\t' + str2

        
