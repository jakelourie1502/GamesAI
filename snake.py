import curses
from random import randint
import time
import numpy as np
import random

class Snake():
    def __init__(self, vert_bounds, hor_bounds, length=3):
        
        #body is the whole snake, comprised of head+tail
        self.direction = randint(0,1)
        x = randint(vert_bounds[0],vert_bounds[1])
        y = randint(hor_bounds[0],hor_bounds[1])
        self.body = [[x+i,y] if self.direction==0 else [x,y+i] for i in range(3) ]
        self.head, self.tail = self.body[0], self.body[1:].copy()
        self.length = length

    def HasEatenItself(self):
        if self.head in self.tail:
            return True
    
    def CheckContigous(self):
        for idx, point in enumerate(self.body[:self.length-2]):
            nextPoint = self.body[idx+1]
            assert abs((point[0]-nextPoint[0]) + (point[1] - nextPoint[1])) == 1, (self.body,self.head,self.tail)

    def grow(self,coor):
        coors = list(coor[:])
        self.length +=1
        self.body.insert(0,coor)
        self.body.pop()
        self.head, self.tail = self.body[0], self.body[1:].copy()
    
    def move(self, coor):     
        self.body = [coor] + self.body
        self.body.pop()
        self.head, self.tail = self.body[0], self.body[1:].copy()
        
        
class SnakeGame:
    def __init__(self, board_width = 20, board_height = 20, gui = False,starting_length=3):
        self.score = 0
        self.done = False
        self.board = {'width': board_width, 'height': board_height}
        self.gui = gui  
        self.starting_length = starting_length
        self.dict_of_pairs()
        self.snake_log = {}
        self.move_log = {}
        self.food_log = {}
        self.CompassDirectionLog = {}
        self.moves = 0
        self.newpointlog = {}
        self.headlog={}
        self.taillog={}        

    def start(self): #this function kicks the game off
        self.snake = Snake([5,self.board["height"] - 5], [5, self.board['width']-5], self.starting_length)
        self.generate_food()
        if self.gui: self.render_init()
        return self.generate_observations()

    def generate_food(self): #this creates a new apple somewhere in the board
        food = []
        while food == []:
            food = [randint(1, self.board["height"]), randint(1, self.board["width"])]
            if food in self.snake.body: food = []
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
        for idx, point in enumerate(self.snake.tail):
            self.win.addch(point[0],point[1],'0')
        self.win.addch(self.snake.head[0],self.snake.head[1],'X')
        self.win.getch()
        

    def dict_of_pairs(self):
        #create mapping between current compass direction and value of new compass direction if you take a certain path
        self.left_dict = {0:3, 3:2,2:1, 1:0} #as above
        self.right_dict = {0:1, 1:2, 2:3, 3:0} #key is current direction, value is new direction
        self.fwd_dict = {0:0, 1:1, 2:2, 3:3}
        self.super_dict_comp_change = {0: self.fwd_dict, 1: self.left_dict, 2: self.right_dict}
        self.reverse_dict = {0:2, 1:3, 2:0, 3:1}
        self.CompassCoorDict = {0:[1,0],1:[0,1],2:[-1,0],3:[0,-1]}
        # #key is current compass direction, value is the change it going e.g. left leads to.
        # self.left_coor_chg = {0:[0,-1],1:[1,0],2:[0,1],3:[-1,0]} 
        # self.right_coor_chg = {0:[0,1],1:[-1,0],2:[0,-1],3:[1,0]} 
        # self.fwd_coor_chg = {0:[1,0], 1:[0,1], 2:[-1,0], 3:[0,-1]}
        # self.super_dict_coor_chg = {0: self.fwd_coor_chg, 1: self.left_coor_chg, 2: self.right_coor_chg} #key here is the facing direction(fwd,left,right) you've chosen to go

    # def choose_step(self): #so this allows us to pick a step relative to the way we're currently facing, and doesn't allow us to go 'backward'
    #     FaceDirectionChoice = self.model() #here we get a 0 (forward), 1(left), 2(right)
        
    #     #select the relevant dict rom the choice, then your current compass direction to retrieve your new compass direction
    #     CompassDirectionChoice = self.super_dict_comp_change[FaceDirectionChoice][self.snake.direction]
    #     print(self.snake.direction, CompassDirectionChoice,FaceDirectionChoice)
    #     return CompassDirectionChoice, FaceDirectionChoice

    #current naive model
    def model(self):
        available_options = [0,1,2,3]
        available_options.remove(self.reverse_dict[self.snake.direction])

        return random.sample(available_options,1)[0]

        # return randint(0,2) #0 - UP, 1, LEFT, 2 - RIGHT

    def step(self):
        # 0 - UP, # 1 - RIGHT, # 2 - DOWN, # 3 - LEFT

        CompassDirectionChoice = self.model()
        if self.done == True: 
            self.end_game()
        self.CreateLogs()
        
        NewPoint = self.create_new_point(CompassDirectionChoice)
        self.snake.direction = CompassDirectionChoice #create a line which tells us which direction the snake is now pointing in
        if self.food_eaten(NewPoint):
            self.score += 1
            self.generate_food()
            self.snake.grow(NewPoint)
        else:
            self.snake.move(NewPoint) 
        self.snake.CheckContigous()
        self.check_collisions()
        if self.gui: self.render()
        # self.done, self.score, self.snake, self.food = self.generate_observations()
        return self.done

    def CreateLogs(self):

        self.snake_log[self.moves] = [x for x in self.snake.body[:]]
        self.headlog[self.moves] =[x for x in self.snake.head[:]]
        self.taillog[self.moves] =[x for x in self.snake.tail[:]]
        # self.move_log[self.moves] = FaceDirectionChoice
        self.food_log[self.moves] = self.food
        self.CompassDirectionLog[self.moves] = self.snake.direction 
        self.moves+=1

    def create_new_point(self, CompassDirectionChoice): 
        #here we take the key 
        new_point = self.snake.head.copy() 
        # added_amount = self.super_dict_coor_chg[FaceDirectionChoice][self.snake.direction] 
        added_amount = self.CompassCoorDict[CompassDirectionChoice]
        new_point[0] +=  added_amount[0]
        new_point[1] += added_amount[1]
        self.newpointlog[self.moves] = [x for x in list(new_point)]
        return new_point

    def food_eaten(self,NewPoint):
        return NewPoint == self.food #this is an assertion. if the front of the snake == food, add one to food.

    def HitBoardEdge(self):
        if (self.snake.head[0]  in (0,self.board["height"]+1)) or (self.snake.head[1]  in (0,self.board["width"]+1)):
            self.moves = 100
            return True

    def check_collisions(self):
        #here we just check the very front of the snake
        if self.HitBoardEdge() or self.snake.HasEatenItself():    
            self.moves=999
            self.CreateLogs()
            self.done = True
        
    def generate_observations(self):
        return self.done, self.score, self.snake, self.food

    def render_destroy(self):
        curses.endwin()

    def end_game(self):
        if self.gui: self.render_destroy()
        
if __name__ == "__main__":
    game = SnakeGame(gui = True,)
    game.start()
    game.render()
    done = False
    for i in range(20):
        
        done = game.step()
        
        if done:
            break

time.sleep(1)
#close the screen
curses.endwin()
print(game.score)
print(done)
print('overall game log: new points')
print(game.newpointlog)    
print('Head')
print(game.headlog)
print('tail')
print(game.taillog)
print('body')
print(game.snake_log)


''''''''''''

# class SnakeGame:
#     def __init__(self, board_width = 20, board_height = 20, gui = False):
#         self.score = 0
#         self.done = False
#         self.board = {'width': board_width, 'height': board_height}
#         self.gui = gui  
#         self.dict_of_pairs()
#         self.snake_log = {}
#         self.moves = 0

#     def start(self): #this function kicks the game off
#         self.snake_init()
#         self.generate_food()
#         if self.gui: self.render_init()
#         return self.generate_observations()

#     def snake_init(self): #this initialises the board in the backend and also decides if the snake (which will be somewhere in the middle) is vertical or horizontal
#         x = randint(5, self.board["width"] - 5)
#         y = randint(5, self.board["height"] - 5)
#         self.snake = []
#         vertical = randint(0,1) == 0
#         for i in range(3):
#             point = [x + i, y] if vertical else [x, y + i]
#             self.direction = 0 if vertical else 1
#             self.snake.insert(0, point)

#     def generate_food(self): #this creates a new apple somewhere in the board
#         food = []
#         while food == []:
#             food = [randint(1, self.board["width"]), randint(1, self.board["height"])]
#             if food in self.snake: food = []
#         self.food = food

#     def render_init(self): #this just initialises curses
#         curses.initscr()
#         win = curses.newwin(self.board["width"] + 2, self.board["height"] + 2, 0, 0)
#         curses.curs_set(0)
#         win.nodelay(1)
#         win.timeout(200)
#         self.win = win #win here is the window
#         self.render()

#     def render(self): #and then this section actually adds the snake board from the backend to the curses window.
#         self.win.clear() 
#         self.win.border(0)
#         self.win.addstr(0, 2, 'Score : ' + str(self.score) + ' ') #adds a score section
#         self.win.addch(self.food[0], self.food[1], '@') #adds the apple in the positions [0](y) and [1](x)
#         for i, point in enumerate(self.snake):
#             if i == 0:
#                 self.win.addch(point[0], point[1], 'X') #sets head of snake
#             else:
#                 self.win.addch(point[0], point[1], 'O') #sets tails of snake
#         self.win.getch()

#     def dict_of_pairs(self):
#         #create mapping between current compass direction and value of new compass direction if you take a certain path
#         self.left_dict = {0:3, 3:2,2:1, 1:0} #as above
#         self.right_dict = {0:1, 1:2, 2:3, 3:0} #key is current direction, value is new direction
#         self.fwd_dict = {0:0, 1:1, 2:2, 3:3}
#         self.super_dict_comp_change = {0: self.left_dict, 1: self.left_dict, 2: self.right_dict}

#         #key is current compass direction, value is the change it leads to 
#         self.left_coor_chg = {0:[0,-1],1:[1,0],2:[0,1],3:[-1,0]} 
#         self.right_coor_chg = {0:[0,1],1:[-1,0],2:[0,-1],3:[1,0]} 
#         self.fwd_coor_chg = {0:[1,0], 1:[0,1], 2:[-1,0], 3:[0,-1]}
#         self.super_dict_coor_chg = {0: self.fwd_coor_chg, 1: self.left_coor_chg, 2: self.right_coor_chg} #key here is the facing direction(fwd,left,right) you've chosen to go

#     def choose_step(self): #so this allows us to pick a step relative to the way we're currently facing, and doesn't allow us to go 'backward'
#         choice = self.model() #here we get a 0 (forward), 1(left), 2(right)

#         #select the relevant dict rom the choice, then your current compass direction to retrieve your new compass direction
#         key = self.super_dict_comp_change[choice][self.direction]
#         return key, choice

#     #current naive model
#     def model(self):
#         return np.random.randint(0,3)

#     def step(self):
#         # 0 - UP
#         # 1 - RIGHT
#         # 2 - DOWN
#         # 3 - LEFT
#         key, choice = self.choose_step()        
#         if self.done == True: 
#             self.end_game()
#         self.create_new_point(key, choice)
#         self.direction = key #create a line which tells us which direction the snake is pointing in
#         if self.food_eaten():
#             self.score += 1
#             self.generate_food()
#         else:
#             self.remove_last_point() #gets rid of the last point
#         self.check_collisions()
#         if self.gui: self.render()
#         self.done, self.score, self.snake, self.food = self.generate_observations()
#         return self.done

#     def create_new_point(self, key, choice): 
#         #here we take the key 
#         new_point = [self.snake[0][0], self.snake[0][1]] #[0][0] is [0] element of the snake list, y axis.
#         added_amount = self.super_dict_coor_chg[choice][self.direction] 
#         new_point[0] +=  added_amount[0]
#         new_point[1] += added_amount[1]
#         #so we take the current forward point of the snake and add/minus 1 to the x/y direction
#         self.snake.insert(0, new_point)
#         self.snake_log[self.moves] = [x for x in self.snake]
#         self.moves+=1
        

#     def remove_last_point(self):
#         self.snake.pop()
#         #just removes the bottom of the tail point

#     def food_eaten(self):
#         return self.snake[0] == self.food #this is an assertion. if the front of the snake == food, add one to food.

#     def check_collisions(self):
#         #here we just check the very front of the snake
#         if (self.snake[0][0] == 0 or
#             self.snake[0][0] == self.board["width"] + 1 or
#             self.snake[0][1] == 0 or
#             self.snake[0][1] == self.board["height"] + 1):
#             self.done = True 
#         elif self.snake[0] in self.snake[1:]:
#             self.done = True

#     def generate_observations(self):
#         return self.done, self.score, self.snake, self.food

#     def render_destroy(self):
#         curses.endwin()

#     def end_game(self):
#         if self.gui: self.render_destroy()
        

# if __name__ == "__main__":
#     game = SnakeGame(gui = True)
#     game.start()
#     game.render()
#     done = False
#     for _ in range(50):
#         while done == False:
#             done = game.step()
#             print(done)
        

# time.sleep(3)
# #close the screen
# curses.endwin()
# print(game.score)
# print(done)
# print('overall game log:')
# print(game.snake_log)    