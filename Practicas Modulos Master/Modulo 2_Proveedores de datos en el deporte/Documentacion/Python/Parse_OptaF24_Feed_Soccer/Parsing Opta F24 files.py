#!/usr/bin/env python
# coding: utf-8

# In[76]:


import csv
import pandas as pd
import xml.etree.ElementTree as et
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Arc
from datetime import datetime as dt


# ### Leer fichero F24 con datos de un partido reemplazar el nombre aquí

# In[43]:


tree = et.ElementTree(file = "f24-23-2018-1009345-eventdetails.xml")
games = tree.getroot()


# In[44]:


match_details = games[0].attrib
match_details


# ## Squads file

# In[12]:


tree3 = et.ElementTree(file = "srml-23-2018-squads.xml")
soccerfeed = tree3.getroot()


# In[39]:


player_ids = []
player_names = []

for child in soccerfeed:
    for grchild in child:
        if grchild.tag == "Team":
            for grgrchild in grchild:
                if grgrchild.tag == "Player":
                    player_ids.append(grgrchild.attrib["uID"].lstrip('p'))                     
                    for kchild in grgrchild:
                            if kchild.tag == "Name":
                                player_names.append(kchild.text)
                        
player_dict = dict(zip(player_ids, player_names))


# #### Ver los primeros 10 elementos del dicccionario de jugadores

# In[41]:


list(player_dict.items())[:10]


# ## Match preview summary

# In[45]:


print ("%s v %s, %s %s" % (match_details["home_team_name"],
                          match_details["away_team_name"],
                          match_details["competition_name"][8:],
                          match_details["season_name"][7:]))


print ("Date: %s" % dt.strftime(dt.strptime(match_details["game_date"], '%Y-%m-%dT%H:%M:%S'),
                               "%A %d %B %Y"))

print ("Kick-off: %s" % dt.strftime(dt.strptime(match_details["game_date"], '%Y-%m-%dT%H:%M:%S'),
                               "%I%p").lstrip("0"))


# ### Equipos diccionario

# In[46]:


team_dict = {match_details["home_team_id"]: match_details["home_team_name"],
             match_details["away_team_id"]: match_details["away_team_name"]}

print (team_dict)


# ## Passes

# In[47]:


# PASSES

passes_x = []
passes_y = []
passes_outcome = []
passes_min = []
passes_sec = []
passes_period = []
passes_team = []
passes_x_end = []
passes_y_end = []
passes_length = []
passes_angle = []
passes_zone = []
pass_real = []
pass_player = []

for game in games:
    for event in game:
        
        if event.attrib.get("type_id") == '1':
            
            passes_x.append(event.attrib.get("x"))
            passes_y.append(event.attrib.get("y"))
            passes_outcome.append(event.attrib.get("outcome"))
            passes_min.append(event.attrib.get("min"))
            passes_sec.append(event.attrib.get("sec"))
            passes_period.append(event.attrib.get("period_id"))
            passes_team.append(team_dict[event.attrib.get("team_id")])
            pass_player.append(player_dict[event.attrib.get("player_id")])
            
            for q in event:
                
                qualifier = q.attrib.get("qualifier_id")
                
                if qualifier == "140":
                    passes_x_end.append(q.attrib.get("value"))
                if qualifier == "141":
                    passes_y_end.append(q.attrib.get("value"))
                if qualifier == "212":
                    passes_length.append(q.attrib.get("value"))
                if qualifier == "213":
                    passes_angle.append(q.attrib.get("value"))
                if qualifier == "56":
                    passes_zone.append(q.attrib.get("value"))
                    
                             
passes_df = np.array(list(zip(passes_team, pass_player, passes_period, passes_min, passes_sec, passes_zone, passes_x, 
                        passes_y, passes_x_end, passes_y_end, passes_length, passes_angle,passes_outcome)))

print (passes_df)

fieldnames = ["team", "player", "period", "min", "sec", "pass zone", "x", "y", "x_end", "y_end",
              "pass length", "pass angle", "outcome"]

with open("pass_data_%s_%s.csv" % (match_details["home_team_name"], match_details["away_team_name"]),"w",newline='') as passes_csv:
        csv_file = csv.writer(passes_csv)
        csv_file.writerow(fieldnames)
        for i in range(len(passes_df)):
            csv_file.writerow(passes_df[i])


# In[48]:


passes_df


# In[64]:


passes = pd.DataFrame(passes_df,columns=["team", "player", "period", "min", "sec", "pass zone", "x", "y", "x_end", "y_end",
              "pass length", "pass angle", "outcome"])


# In[68]:


passes['period'] = passes['period'].astype('int64')
passes['min'] = passes['min'].astype('int64')
passes['sec'] = passes['sec'].astype('int64')
passes['x'] = passes['x'].astype('float64')
passes['y'] = passes['y'].astype('float64')
passes['x_end'] = passes['x_end'].astype('float64')
passes['y_end'] = passes['y_end'].astype('float64')
passes['pass length'] = passes['pass length'].astype('float64')
passes['pass angle'] = passes['pass angle'].astype('float64')
passes['outcome'] = passes['outcome'].astype('int64')


# In[69]:


passes.dtypes


# In[71]:


passes.head(15)


# Filtramos los pases de un jugador Karim Benzema

# In[75]:


pasesJugador= passes.loc[passes['player'] == "Karim Benzema"]

pasesJugador= pasesJugador.reset_index()

pasesJugador.head(10)


# In[ ]:





# In[81]:


fig=plt.figure()
fig.set_size_inches(12, 9) # Cambiar aqui el tamaño (Ancho, Alto)
ax=fig.add_subplot(1,1,1)

# Pitch Outline & Centre Line OK
plt.plot([0,0],[0,100], color="black")
plt.plot([0,100],[100,100], color="black") #upper line x_start x_end y_start y_end
plt.plot([100,100],[100,0], color="black")
plt.plot([100,0],[0,0], color="black")
plt.plot([50,50],[0,100], color="black")

# Left Penalty Area OK
plt.plot([17,17],[78.9,21.1],color="black")
plt.plot([0,17],[78.9,78.9],color="black")
plt.plot([17,0],[21.1,21.1],color="black")

# Right Penalty Area OK
plt.plot([100,83],[78.9,78.9],color="black")
plt.plot([83,83],[78.9,21.1],color="black")
plt.plot([83,100],[21.1,21.1],color="black")

# Left 6-yard Box on testing
plt.plot([0,5.8],[63.2,63.2],color="black")
plt.plot([5.8,5.8],[63.2,36.8],color="black")
plt.plot([5.8,0],[36.8,36.8],color="black")

# Right 6-yard Box on testing
plt.plot([100,94.2],[63.2,63.2],color="black")
plt.plot([94.2,94.2],[63.2,36.8],color="black")
plt.plot([94.2,100],[36.8,36.8],color="black")

# Prepare Circles OK
centreCircle = plt.Circle((50,50),9.15,color="black",fill=False)
centreSpot = plt.Circle((50,50),0.7,color="black")
leftPenSpot = plt.Circle((11.5,50),0.7,color="black")
rightPenSpot = plt.Circle((88.5,50),0.7,color="black")

# Draw Circles
ax.add_patch(centreCircle)
ax.add_patch(centreSpot)
ax.add_patch(leftPenSpot)
ax.add_patch(rightPenSpot)

# Prepare Arcs based on penalty Spots 
leftArc = Arc((11.5,50),height=18.3,width=18.3,angle=0,theta1=310,theta2=50,color="black")
rightArc = Arc((88.5,50),height=18.3,width=18.3,angle=0,theta1=130,theta2=230,color="black")

# leftArc = Arc((17,50),height=18.3,width=18.3,angle=0,theta1=310,theta2=50,color="blue")
# rightArc = Arc((83,50),height=18.3,width=18.3,angle=0,theta1=130,theta2=230,color="red")

# Draw Arcs
ax.add_patch(leftArc)
ax.add_patch(rightArc)

# Tidy Axes
plt.axis('off')

####################
# PLOT PASSES
####################

for i in range(len(pasesJugador)):
    color = "green" if pasesJugador.iloc[i]['outcome'] == 1 else "red"
    plt.plot([int(pasesJugador["x"][i]),int(pasesJugador["x_end"][i])],
             [int(pasesJugador["y"][i]),int(pasesJugador["y_end"][i])], color=color)
    plt.plot(int(pasesJugador["x"][i]),int(pasesJugador["y"][i]),"o", color=color)


#Display Pitch
# plt.tight_layout()
plt.show()


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# ## Goals

# In[94]:


# GOALS
goal_x = []
goal_y = []
goal_zone = []
goal_outcome = []
goal_min = []
goal_sec = []
goal_period = []
goal_team = []
goalmouth_y = []
goalmouth_z = []
goal_assisted = []
body_part = []
goal_player = []

body_dict = {"15": "head",
            "72": "left foot",
            "20": "right foot",
            "21": "other body part"}

for game in games:
    for event in game:
        
        if event.attrib.get("type_id") == '16':
            
            goal_x.append(event.attrib.get("x"))
            goal_y.append(event.attrib.get("y"))
            goal_outcome.append(event.attrib.get("outcome"))
            goal_min.append(event.attrib.get("min"))
            goal_sec.append(event.attrib.get("sec"))
            goal_period.append(event.attrib.get("period_id"))
            goal_team.append(team_dict[event.attrib.get("team_id")])
            goal_player.append(player_dict[event.attrib.get("player_id")])
            
            for q in event:
                
                qualifier = q.attrib.get("qualifier_id")
                
                
                if qualifier == "103":
                    goalmouth_z.append(q.attrib.get("value"))
                if qualifier == "102":
                    goalmouth_y.append(q.attrib.get("value"))
                if qualifier == "56":
                    goal_zone.append(q.attrib.get("value"))
                if qualifier in ["15", "72", "20", "21"]:
                    body_part.append(body_dict[qualifier])
                
                
                             
goal_df = np.array(list(zip(goal_team, goal_player, goal_period, goal_min, goal_sec, body_part, goal_zone, goal_x, 
                         goal_y, goalmouth_y, goalmouth_z, goal_outcome)))
print (goal_df)

goal_fieldnames = ["team", "player", "period", "min", "sec", "body part", "zone", "x", "y", 
                   "goalmouth y", "goalmouth z", "outcome"]

with open("goal_data_%s_%s.csv" % (match_details["home_team_name"], match_details["away_team_name"]),"w",newline='') as goal_csv:
        csv_file = csv.writer(goal_csv)
        csv_file.writerow(goal_fieldnames)
        for i in range(len(goal_df)):
            csv_file.writerow(goal_df[i])


# In[98]:


goal = pd.DataFrame(goal_df,columns=["team", "player", "period", "min", "sec", "body part", "zone", "x", "y", 
                   "goalmouth y", "goalmouth z", "outcome"])


# In[99]:


goal


# In[101]:


goal['period'] = goal['period'].astype('int64')
goal['min'] = goal['min'].astype('int64')
goal['sec'] = goal['sec'].astype('int64')
goal['x'] = goal['x'].astype('float64')
goal['y'] = goal['y'].astype('float64')
goal['goalmouth y'] = goal['goalmouth y'].astype('float64')
goal['goalmouth z'] = goal['goalmouth z'].astype('float64')
goal['outcome'] = goal['outcome'].astype('int64')


# In[102]:


goal.dtypes


# ## Plot goals

# In[107]:


fig=plt.figure()
fig.set_size_inches(12, 9) # Cambiar aqui el tamaño (Ancho, Alto)
ax=fig.add_subplot(1,1,1)

# Pitch Outline & Centre Line OK
plt.plot([0,0],[0,100], color="black")
plt.plot([0,100],[100,100], color="black") #upper line x_start x_end y_start y_end
plt.plot([100,100],[100,0], color="black")
plt.plot([100,0],[0,0], color="black")
plt.plot([50,50],[0,100], color="black")

# Left Penalty Area OK
plt.plot([17,17],[78.9,21.1],color="black")
plt.plot([0,17],[78.9,78.9],color="black")
plt.plot([17,0],[21.1,21.1],color="black")

# Right Penalty Area OK
plt.plot([100,83],[78.9,78.9],color="black")
plt.plot([83,83],[78.9,21.1],color="black")
plt.plot([83,100],[21.1,21.1],color="black")

# Left 6-yard Box on testing
plt.plot([0,5.8],[63.2,63.2],color="black")
plt.plot([5.8,5.8],[63.2,36.8],color="black")
plt.plot([5.8,0],[36.8,36.8],color="black")

# Right 6-yard Box on testing
plt.plot([100,94.2],[63.2,63.2],color="black")
plt.plot([94.2,94.2],[63.2,36.8],color="black")
plt.plot([94.2,100],[36.8,36.8],color="black")

# Prepare Circles OK
centreCircle = plt.Circle((50,50),9.15,color="black",fill=False)
centreSpot = plt.Circle((50,50),0.7,color="black")
leftPenSpot = plt.Circle((11.5,50),0.7,color="black")
rightPenSpot = plt.Circle((88.5,50),0.7,color="black")

# Draw Circles
ax.add_patch(centreCircle)
ax.add_patch(centreSpot)
ax.add_patch(leftPenSpot)
ax.add_patch(rightPenSpot)

# Prepare Arcs based on penalty Spots 
leftArc = Arc((11.5,50),height=18.3,width=18.3,angle=0,theta1=310,theta2=50,color="black")
rightArc = Arc((88.5,50),height=18.3,width=18.3,angle=0,theta1=130,theta2=230,color="black")

# leftArc = Arc((17,50),height=18.3,width=18.3,angle=0,theta1=310,theta2=50,color="blue")
# rightArc = Arc((83,50),height=18.3,width=18.3,angle=0,theta1=130,theta2=230,color="red")

# Draw Arcs
ax.add_patch(leftArc)
ax.add_patch(rightArc)

# Tidy Axes
plt.axis('off')

####################
# PLOT PASSES
####################

for i in range(len(goal)):
    #color = "green" if goal.iloc[i]['outcome'] == 1 else "red"
    plt.plot([int(goal["x"][i]),100],  # LA X final de los goles es la linea de gol x=100
             [int(goal["y"][i]),int(goal["goalmouth y"][i])])
    #plt.plot(int(goal["x"][i]),int(goal["y"][i]),"o")


#Display Pitch
# plt.tight_layout()
plt.show()


# In[ ]:





# ## ALL SHOTS

# In[117]:


# ALL SHOTS

shot_name = []
shot_x = []
shot_y = []
shot_zone = []
shot_min = []
shot_sec = []
shot_period = []
shot_team = []
goalmouth_y = []
goalmouth_z = []
saved_x = []
saved_y = []
body_part = []
shot_play = []
shot_player = []

shot_dict = {'13': 'Shot off target',
             '14': 'Post',
             '15': 'Shot saved',
             '16': 'Goal'}

body_dict = {"15": "head",
            "72": "left foot",
            "20": "right foot",
            "21": "other body part"}

shot_play_dict = {'22': 'regular play',
            '23': 'fast break',
            '24': 'set piece',
            '25': 'from corner',
            '26': 'free kick',
            '96': 'corner situation',
            '112': 'scramble',
            '160': 'throw-in set piece',
            '9': 'penalty',
            '28': 'own goal'}

for game in games:
    
    for event in game:
        
        if event.attrib.get("type_id") in ['13', '14', '16']:
                    
            shot_name.append(shot_dict[event.attrib.get("type_id")])
            shot_x.append(event.attrib.get("x"))
            shot_y.append(event.attrib.get("y"))
            shot_min.append(event.attrib.get("min"))
            shot_sec.append(event.attrib.get("sec"))
            shot_period.append(event.attrib.get("period_id"))
            shot_team.append(team_dict[event.attrib.get("team_id")])
            shot_player.append(player_dict[event.attrib.get("player_id")])
            
            for q in event:
                
                qualifier = q.attrib.get("qualifier_id")
                if qualifier == '102':
                    saved_x.append('')
                    saved_y.append('')
                    goalmouth_y.append(q.attrib.get("value"))
                if qualifier == '103':
                    goalmouth_z.append(q.attrib.get("value"))
                if qualifier in body_dict.keys():
                    body_part.append(body_dict[qualifier])
                if qualifier in shot_play_dict.keys():
                    shot_play.append(shot_play_dict[qualifier])
                                   
        if event.attrib.get("type_id") == '15':
                    
            shot_name.append(shot_dict[event.attrib.get("type_id")])
            shot_x.append(event.attrib.get("x"))
            shot_y.append(event.attrib.get("y"))
            shot_min.append(event.attrib.get("min"))
            shot_sec.append(event.attrib.get("sec"))
            shot_period.append(event.attrib.get("period_id"))
            shot_team.append(team_dict[event.attrib.get("team_id")])
            shot_player.append(player_dict[event.attrib.get("player_id")])
                        
            
            for q in event:
                
                qualifier = q.attrib.get("qualifier_id")
                if qualifier == '146':
                    goalmouth_y.append('')
                    goalmouth_z.append('')
                    saved_x.append(q.attrib.get("value"))
                if qualifier == '147':
                    saved_y.append(q.attrib.get("value"))
                if qualifier in ["15", "72", "20", "21"]:
                    body_part.append(body_dict[qualifier])
                if qualifier in shot_play_dict.keys():
                    shot_play.append(shot_play_dict[qualifier])
                               
                             
shot_df = np.array(list(zip(shot_team, shot_player, shot_period, shot_min, shot_sec, shot_play, shot_name, body_part, shot_x, shot_y, 
                       goalmouth_y, goalmouth_z, saved_x, saved_y)))
    
# print (shot_df)

shot_fieldnames = ["team", "player", "period", "min", "sec", "shot play", "shot type", "body part", "x", "y", "goalmouth y", 
                   "goalmouth z", "saved x", "saved y"]

with open("shot_data_%s_%s.csv" % (match_details["home_team_name"], match_details["away_team_name"]), 
          "w",newline='') as shot_csv:
        csv_file = csv.writer(shot_csv)
        csv_file.writerow(shot_fieldnames)
        for i in range(len(shot_df)):
            csv_file.writerow(shot_df[i])


# In[128]:


shot = pd.DataFrame(shot_df,
columns=["team", "player", "period", "min", "sec", "shot play", "shot type", 
         "body part", "x", "y", "shotmouth y","shotmouth z", "saved x", "saved y"])


# In[129]:


shot.head(10)


# In[133]:


shot['period'] = shot['period'].astype('int64')
shot['min'] = shot['min'].astype('int64')
shot['sec'] = shot['sec'].astype('int64')
shot['x'] = shot['x'].astype('float64')
shot['y'] = shot['y'].astype('float64')
shot['shotmouth y'] = pd.to_numeric(shot['shotmouth y'],errors='ignore')
shot['shotmouth z'] = pd.to_numeric(shot['shotmouth z'],errors='ignore')
shot['saved x']     = pd.to_numeric(shot['saved x'],errors='ignore')
shot['saved y']     = pd.to_numeric(shot['saved y'],errors='ignore')


# In[134]:


shot.dtypes


# In[135]:


shot.head(10)


# In[ ]:




