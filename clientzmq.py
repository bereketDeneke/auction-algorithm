from __future__ import print_function #I added this because it made my life a lot easier when
#the 'end = ...' function was added in the print function that I didn't know a nice way to do
#in Python 2.7, so print statements must all have brackets in this version, no need in the server though
# Echo client program
import zmq
import random
import time
import os
import platform


# # to act as a client
port = "50018"              # The server port
context = zmq.Context()
print ("Connecting to server...")
socket = context.socket(zmq.REQ)
socket.connect ("tcp://localhost:%s" % port)

# APPLICATION
partnerid = -1 # no partner
numberbidders = 0 # will be given by server
artists = ['Picasso', 'Rembrandt', 'Van_Gogh', 'Da_Vinci']

# DO SOMETHING HERE
# you need to change this to do something much more clever
game_info = []
check_round = 0

check_round = 0
curr_round_art = ""
def determinebid(itemsinauction:list, winnerarray:list, winneramount:list, numberbidders:int, players:list, mybidderid:str, artists:list, standings:dict, round:int):
  total_bid_round = 3 
  check_range = 25 if numberbidders > 5 else 15
  global check_round
  global curr_round_art
  
  try:
    if round % check_range == 0:
      if check_round >= len(itemsinauction):
        typearray = itemsinauction[len(itemsinauction) - check_range: ]
      else:
        typearray = itemsinauction[check_round: sum([check_round, check_range])]
    
      # counting the number of items
      item_freq = [typearray.count(item) for item in artists]
      
      # calculating the average distance of the items in auction
      mean = lambda f: sum(f) / len(f) if len(f) > 0 else 10000 
      xcute = lambda x: mean([i for i in range(len(typearray)) if typearray[i] == x and item_freq[artists.index(x)] >= total_bid_round])
      item_destr = [xcute(item) for item in artists]
      
      # the art/item we are bidding for
      curr_round_art = artists[item_destr.index(min(item_destr))]

      # adjust the range if it can't bid for at least one item during the first check_range rounds
      if standings[mybidderid][curr_round_art] == 0 and (round + 1) >= check_range:
        check_round += check_range

    if curr_round_art == itemsinauction[round]:
      return min(int(100//3) + (curr_round_art == itemsinauction[round] and standings[mybidderid][curr_round_art] == 0), moneyleft)
    
    # blocking the opponent
    for standing in standings.keys():
      if standings[standing][itemsinauction[round]] >= 2: return random.randint(6, 13)
    return 0
  except Exception as er:
    print("Error ", str(er))
    return 0 
 
mybidderid = "Hunters"
while len(mybidderid) == 0 or ' ' in mybidderid:
  mybidderid = input("You input an empty string or included a space in your name which is not allowed (_ or / are all allowed)\n for example Emil_And_Nischal is okay\nInput team / player name: ").strip()

moneyleft = 100 # Should change over time
winnerarray = [] # Who won each round
winneramount = [] # How much they paid

itemsinauction = []
myTypes = {'Picasso': 0, 'Rembrandt': 0, 'Van_Gogh': 0, 'Da_Vinci': 0, 'money': moneyleft}

# EXECUTION

# get list of items and types
getlistflag = 1
socket.send((str(mybidderid)).encode())
while(getlistflag == 1):
  data = socket.recv(5024)
  x = (data.decode("utf-8")).split(" ")
  # print "Have received response at ", str(mybidderid), " of: ", ' '.join(x)
  #Receives first how many players are in the game and then all 200 items in auction
  if(x[0] != "Not" and len(data) != 0):
    getlistflag = 0
    numberbidders = int(x[0])
    itemsinauction = x[1:]

while True:
  socket.send((str(mybidderid) + ' ').encode())
  data = socket.recv(5024)
  x = (data.decode("utf-8")).split(" ")
  #Wait until everyone has connected before bidding
  if (x[0] == 'wait'):
    continue
  #When everyone has connected the server knows all names
  #it can therefore transfer all the names after telling the client that it's ready
  players = []
  for player in range(1, numberbidders + 1):
    players.append(x[player])
  break
#Create initial standings for each player after everyone connected
standings = {name: {'Picasso': 0, 'Van_Gogh': 0, 'Rembrandt': 0, 'Da_Vinci': 0, 'money': 100} for name in players}
# now do bids
continueflag = 1
j = 0
if platform.system() == 'Windows':
  os.system('cls')
else:
  os.system('clear')
while(continueflag == 1):
  #roundStart = time.time()
  print(random.choice(["I'm doing my best, okay?", "Why aren't you cheering louder?", "Aren't you proud of me?", "Damn I'm good, and I don't even have a brain!", "And do you think you could do any better?", "I feel like it's me doing all the work, you're just chilling in your chair", "If I lose this it's your fault not mine... I'm doing EXACTLY what you told me to do!"]))
  print()
  bidflag = 1
  bid = determinebid(itemsinauction, winnerarray, winneramount, numberbidders, players, mybidderid, artists, standings, len(winnerarray))
  #sleep before sending the bid to make sure the server is ready, currently it's at a very big value 1
  #this should make it safe for any speed of computers or internet, but can probably be lower as I have had
  #it working on Wifi with my computer at 0.2
  socket.send((str(mybidderid) + " " + str(bid)).encode())
  while(bidflag == 1):
    # print "Have sent data from ", str(mybidderid)
    data = socket.recv(5024)
    x = (data.decode("utf-8")).split(" ")
    # print "Have received response at ", str(mybidderid), " of: ", ' '.join(x)
    if(x[0] != "Not"):
      bidflag = 0
    else:
      print("exception")


  resultflag = 1
  while(resultflag == 1):
    socket.send((str(mybidderid)).encode())
    # print "Have sent data from ", str(mybidderid)
    data = socket.recv(5024)
    x = (data.decode("utf-8")).split(" ")
    #Wait for all bids to be received
    if (x[0] == 'wait'):
      continue
    # print "Have received response at ", str(mybidderid), " of: ", ' '.join(x)
    #Check if the server told client that game is finished
    if len(x) >= 7 and x[7] == 'won.':
      time.sleep(5)
      continueflag = 0
      resultflag = 0
      print(data)
      print()
      print('game over')
    #Else update standings, winnerarray etc.
    if(x[0] != "ready") and (continueflag == 1):
      #roundLength = time.time()-roundStart
      #time.sleep(max(0, 5-roundLength))
      resultflag = 0
      if platform.system() == 'Windows':
        os.system('cls')
      else:
        os.system('clear')
      # print x
      winnerarray.append(x[0])
      winneramount.append(int(x[5]))
      standings[x[0]]['money'] -= int(x[5])
      standings[x[0]][x[3]] += 1
      if (x[0] == mybidderid):
        moneyleft -= int(x[5])
        myTypes[itemsinauction[j]] += 1
      # update moneyleft, winnerarray
    else:
      time.sleep(2)
  j+= 1
