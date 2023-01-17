#!/usr/bin/env python
# Echo server program
import select
import zmq
import sys
import random
import time
import os
import platform
import pprint


bot = True #This will change the interface and a few sleep statements of the server, it has two settings
#one for bot play and one for manual play
numbidders = 9 #change this for how many bots you want to play with
HOST = 'localhost' #change this to your own IP address if you want to use it over LAN/Wifi

# if platform.system() == 'Windows':
#   os.system('cls')
# else:
#   os.system('clear')
if not bot:
  print( "Server initiated, waiting for players to connect.\n")
else:
  print("Server initiated, waiting for bots to connect.\n")


port = "50018"              # Arbitrary non-privileged port
context = zmq.Context()
socket = context.socket(zmq.REP)
port = "50018" 
socket.bind("tcp://*:%s" % port)
bidderids = []
neededtowin = 3 # how many items each player needs to win
itemtypes = ['Picasso', 'Van_Gogh', 'Rembrandt', 'Da_Vinci'] # four different types
maxbudget = 100 # budget per player
won = {}
listtosend = str(numbidders) + ' '
typearray = []
i = 0
#Generate itemsinauction and string containing number of bidders and 
#items in auction list to send to the client
while(i < 200):
  x = itemtypes[int((len(itemtypes))*random.random())]
  typearray.append(x)
  listtosend = listtosend + x + ' '
  i+= 1

# distribute list to send to everyone
bidderids = []
readybidders = []
flag1 = True
#Outer loop waits until every client has been told that the server is
#ready to receive bids
while(numbidders > len(readybidders)):
      tdata = socket.recv(1024)
      data = tdata.decode("utf-8")
      if not data: 
        print("Have not received data from"+ str(s))
      indata = data.split(" ")
      # print ' '.join(indata)
      if(indata[0] in bidderids):
        #Waits until all bidders have connected, and then
        #starts telling clients that the server is ready to recieve bids
        if len(bidderids) == numbidders:
          if flag1:
            if not bot:
              print("everyone has connected, let's go!\n")
            else:
              print("everyone has connected, let the Bot Battles begin!")
            time.sleep(2)
            flag1 = False
          if indata[0] in readybidders:
            pass
          else:
            #If first time telling client they are ready send list of names of players
            stringtosend = 'ready '
            for name in bidderids:
              stringtosend += name + ' '
            socket.send(stringtosend.encode())
            readybidders.append(indata[0])
        else:
          #Tell the client to wait if still waiting for people to connect
          socket.send(('wait ').encode())
        #s.send("Not ready " + indata[0] )
      else:
        #If they just connected first time, send the string with
        #number of bidders and items in auction
        socket.send(listtosend.encode())
        bidderids.append(indata[0])
        print(indata[0]+ " joined the game")

won['Picasso'] = {name: 0 for name in bidderids}
won['Van_Gogh'] = {name: 0 for name in bidderids}
won['Rembrandt'] = {name: 0 for name in bidderids}
won['Da_Vinci'] = {name: 0 for name in bidderids}
moneyspent = {name: 0 for name in bidderids}
players = bidderids
doneflag = 0 # will be done only if someone wins or goes over budget with money spent
j = 0
while(0 == doneflag):
  # if platform.system() == 'Windows':
  #   os.system('cls')
  # else:
  #   os.system('clear')
  #generate list to decide when to tell people to hurry up
  start = time.time()
  hurried = [False for i in range(201)]
  hurried[20] = True
  for i in range(20, 201, 10):
    hurried[i] = True
  print("Auction round"+ str(j+1) + ":")
  print()
  if not bot:
    if j != 0:
      print(str(winnerid)+ " bought a "+ str(mytype) + "for "+ str(bestbid))
      print()
    print("Current standings are:\n")
    for player in players:
      tmpdict = {'money': 100-moneyspent[player], 'Picasso': won['Picasso'][player], "Rembrandt": won['Rembrandt'][player], "Da_Vinci": won['Da_Vinci'][player], "Van_Gogh": won['Van_Gogh'][player]}
      print(str(player) + ':') 
      pprint.pprint(tmpdict)
    print()
  mytype = typearray[j]
  print("We are currently bidding for a "+ str(mytype) + '.')
  print()
  bidderids = []
  bids = []
  flag2 = True
  #Keep checking for bids until all are received
  #And tell people to hurry up if it is not a bot round
  while(numbidders > len(bidderids)):
        tdata = socket.recv(1024)
        data = tdata.decode("utf-8")
        if not data: 
          print("Have not received data from "+ str(s))
        indata = data.split(" ")
        #print('indata: '+ ' '.join(indata))
        #Tell the client to wait until all bids have been received
        if(indata[0] in bidderids):
          socket.send(('wait ').encode())
        else:
          if not indata[1].isnumeric():
            x = -2
          else:
            x = int(indata[1])
          if (x > (maxbudget - moneyspent[indata[0]])):
            x = -1 # indata[0] is not allowed to bid over budget
          bids.append(x)
          bidderids.append(indata[0])
          socket.send(('bid received').encode())
          if not bot:
            print("received bid of "+ " from "+ indata[0])
          else:
            print("received bid of "+ str(x) + " from "+ indata[0])
            print()
  # Now have all the bids
  bestbid = max(bids)
  # print "Here are the identifiers of the bidders " 
  # print bidderids
  # print "Here are the bids "
  # print bids
  #winnerid=bidderids[random.choice([x for x in range(len(bids)) if bids[x]==bestbid])]
  winnerid = bidderids[bids.index(bestbid)]
  won[mytype][winnerid]+= 1
  moneyspent[winnerid]+= bestbid
  if bot:
    time.sleep(1.5)
    print()
    print(str(winnerid)+ " bought a "+ str(mytype)+ " for "+ str(bestbid))
    print()
    time.sleep(2)
    print()
    print("Current standings are:\n")
    for player in players:
      tmpdict = {'money': 100-moneyspent[player], 'Picasso': won['Picasso'][player], "Rembrandt": won['Rembrandt'][player], "Da_Vinci": won['Da_Vinci'][player], "Van_Gogh": won['Van_Gogh'][player]}
      print(player + ':')
      pprint.pprint(tmpdict)
    print()
    time.sleep(6)
  if (won[mytype][winnerid] >= neededtowin):
    doneflag = 1
    # if platform.system() == 'Windows':
    #   os.system('cls')
    # else:
    #   os.system('clear')
    print(str(winnerid) + " has won.")
    print("Please close all child processes and this one")
  # Now receive requests for results
  deletedindexes = [] # record which indexes are gone
  while(numbidders > len(deletedindexes)):
        tdata = socket.recv(1024)
        data = tdata.decode("utf-8")
        if not data: 
          print("Have not received data from"+ str(s))
        indata = data.split(" ")
        myindex = bidderids.index(indata[0])
        if(myindex not in deletedindexes):
          deletedindexes.append(myindex)
          #receive results
          if(doneflag == 1):
            socket.send((winnerid + ' has bought ' + mytype + ' for ' + str(bestbid) + ' and won.').encode())
          else:
            socket.send((winnerid + ' has bought ' + mytype + ' for ' + str(bestbid)).encode())
        else:
          socket.send(('ready').encode())
  j+=1

time.sleep(20)
