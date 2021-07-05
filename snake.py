import curses
from random import randint
import time
import numpy as np

class SnakeGame:
    def __init__(self, board_width = 20, board_height = 20, gui = False):
        self.score = 0
        self.done = False
        self.board = {'width': board_width, 'height': board_height}
        self.gui = gui
        self.dict_of_pairs()
        self.snake_log = {}
        self.moves = 0

    def start(self): #this function kicks the game off
        self.snake_init()
        print(self.snake)
        self.generate_food()
        if self.gui: self.render_init()
        return self.generate_observations()

    def snake_init(self): #this initialises the board in the backend and also decides if the snake (which will be somewhere in the middle) is vertical or horizontal
        x = randint(5, self.board["width"] - 5)
        y = randint(5, self.board["height"] - 5)
        self.snake = []
        vertical = randint(0,1) == 0
        for i in range(3):
            point = [x + i, y] if vertical else [x, y + i]
            self.direction = 0 if vertical else 1
            self.snake.insert(0, point)

    def generate_food(self): #this creates a new apple somewhere in the board
        food = []
        while food == []:
            food = [randint(1, self.board["width"]), randint(1, self.board["height"])]
            if food in self.snake: food = []
        self.food = food

    def render_init(self): #this just initialises curses
        curses.initscr()
        win = curses.newwin(self.board["width"] + 2, self.board["height"] + 2, 0, 0)
        curses.curs_set(0)
        win.nodelay(1)
        win.timeout(200)
        self.win = win #win here is the window
        self.render()

    def render(self): #and then this section actually adds the snake board from the backend to the curses window.
        self.win.clear() 
        self.win.border(0)
        self.win.addstr(0, 2, 'Score : ' + str(self.score) + ' ') #adds a score section
        self.win.addch(self.food[0], self.food[1], '@') #adds the apple in the positions [0](y) and [1](x)
        for i, point in enumerate(self.snake):
            if i == 0:
                self.win.addch(point[0], point[1], 'X') #sets head of snake
            else:
                self.win.addch(point[0], point[1], 'O') #sets tails of snake
        self.win.getch()

    def dict_of_pairs(self):
        #create mapping between current compass direction and value of new compass direction if you take a certain path
        self.left_dict = {0:3, 3:2,2:1, 1:0} #as above
        self.right_dict = {0:1, 1:2, 2:3, 3:0} #key is current direction, value is new direction
        self.fwd_dict = {0:0, 1:1, 2:2, 3:3}
        self.super_dict_comp_change = {0: self.left_dict, 1: self.left_dict, 2: self.right_dict}

        #key is current compass direction, value is the change it leads to 
        self.left_coor_chg = {0:[0,-1],1:[1,0],2:[0,1],3:[-1,0]} 
        self.right_coor_chg = {0:[0,1],1:[-1,0],2:[0,-1],3:[1,0]} 
        self.fwd_coor_chg = {0:[1,0], 1:[0,1], 2:[-1,0], 3:[0,-1]}
        self.super_dict_coor_chg = {0: self.fwd_coor_chg, 1: self.left_coor_chg, 2: self.right_coor_chg} #key here is the facing direction(fwd,left,right) you've chosen to go

    def choose_step(self): #so this allows us to pick a step relative to the way we're currently facing, and doesn't allow us to go 'backward'
        choice = self.model() #here we get a 0 (forward), 1(left), 2(right)

        #select the relevant dict rom the choice, then your current compass direction to retrieve your new compass direction
        key = self.super_dict_comp_change[choice][self.direction]
        return key, choice

    #current naive model
    def model(self):
        return np.random.randint(0,3)

    def step(self):
        # 0 - UP
        # 1 - RIGHT
        # 2 - DOWN
        # 3 - LEFT
        key, choice = self.choose_step()        
        if self.done == True: 
            self.end_game()
        self.create_new_point(key, choice)
        self.direction = key #create a line which tells us which direction the snake is pointing in
        if self.food_eaten():
            self.score += 1
            self.generate_food()
        else:
            self.remove_last_point() #gets rid of the last point
        self.check_collisions()
        if self.gui: self.render()
        self.done, self.score, self.snake, self.food = self.generate_observations()
        return self.done

    def create_new_point(self, key, choice): 
        #here we take the key 
        new_point = [self.snake[0][0], self.snake[0][1]] #[0][0] is [0] element of the snake list, y axis.
        added_amount = self.super_dict_coor_chg[choice][self.direction] 
        new_point[0] +=  added_amount[0]
        new_point[1] += added_amount[1]
        #so we take the current forward point of the snake and add/minus 1 to the x/y direction
        self.snake.insert(0, new_point)
        self.snake_log[self.moves] = [x for x in self.snake]
        self.moves+=1
        

    def remove_last_point(self):
        self.snake.pop()
        #just removes the bottom of the tail point

    def food_eaten(self):
        return self.snake[0] == self.food #this is an assertion. if the front of the snake == food, add one to food.

    def check_collisions(self):
        #here we just check the very front of the snake
        if (self.snake[0][0] == 0 or
            self.snake[0][0] == self.board["width"] + 1 or
            self.snake[0][1] == 0 or
            self.snake[0][1] == self.board["height"] + 1):
            self.done = True 
        elif self.snake[0] in self.snake[1:]:
            self.done = True

    def generate_observations(self):
        return self.done, self.score, self.snake, self.food

    def render_destroy(self):
        curses.endwin()

    def end_game(self):
        if self.gui: self.render_destroy()
        

if __name__ == "__main__":
    game = SnakeGame(gui = True)
    game.start()
    game.render()
    done = False
    for _ in range(50):
        while done == False:
            done = game.step()
            print(done)
        

time.sleep(3)
#close the screen
curses.endwin()
print(done)
print('overall game log:')
print(game.snake_log)    