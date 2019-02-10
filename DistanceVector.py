# Project 3 for CS 6250: Computer Networks
#
# This defines a DistanceVector (specialization of the Node class)
# that can run the Bellman-Ford algorithm. The TODOs are all related 
# to implementing BF. Students should modify this file as necessary,
# guided by the TODO comments and the assignment instructions. This 
# is the only file that needs to be modified to complete the project.
#
# Student code should NOT access the following members, otherwise they may violate
# the spirit of the project:
#
# topolink (parameter passed to initialization function)
# self.topology (link to the greater topology structure used for message passing)
#
# Copyright 2017 Michael D. Brown
# Based on prior work by Dave Lillethun, Sean Donovan, and Jeffrey Randow.
        											
from Node import *
from helpers import *
import re
import time

class DistanceVector(Node):
    
    def __init__(self, name, topolink, outgoing_links, incoming_links):
        ''' Constructor. This is run once when the DistanceVector object is
        created at the beginning of the simulation. Initializing data structure(s)
        specific to a DV node is done here.'''

        super(DistanceVector, self).__init__(name, topolink, outgoing_links, incoming_links)
        #TODO: Create any necessary data structure(s) to contain the Node's internal state / distance vector data    
        self.in_state = dict()
        self.in_state["nodes"]={"{}".format(self.name):0}
        self.in_state["vector"]=set(["{name}{distance}".format(name=self.name, distance=0)])
        self.in_state["is_updated"]=True

    def send_initial_messages(self):
        ''' This is run once at the beginning of the simulation, after all
        DistanceVector objects are created and their links to each other are
        established, but before any of the rest of the simulation begins. You
        can have nodes send out their initial DV advertisements here. 

        Remember that links points to a list of Neighbor data structure.  Access
        the elements with .name or .weight '''

        # TODO - Each node needs to build a message and send it to each of its neighbors
        # HINT: Take a look at the skeleton methods provided for you in Node.py
        #print("node {} incoming {}".format(self.name, [n.name for n in self.incoming_links]))
        for node in self.incoming_links:
            message = (self.name, "{node_name}{distance_cost}".format(node_name=self.name, distance_cost=0))
            print("Initial send from {} to {} {}".format(self.name, node.name, message))
            self.send_msg(message, node.name)


    def process_BF(self):
        ''' This is run continuously (repeatedly) during the simulation. DV
        messages from other nodes are received here, processed, and any new DV
        messages that need to be sent to other nodes as a result are sent. '''
        # Implement the Bellman-Ford algorithm here.  It must accomplish two tasks below:
        # TODO 1. Process queued messages 
        print self.name, self.in_state, self.messages
        for msg in self.messages:            
            received_from, vector = msg
            for vector_bit in vector.split(','):
                node, weight, _ = re.split(r'(-?[0-9]+)', vector_bit)
                if node in [n.name for n in self.outgoing_links]:
                    weight = int(self.get_outgoing_neighbor_weight(node))
                    if weight != self.in_state["nodes"].get(node, float("Inf")):
                        self.in_state["nodes"][node] = int(weight)
                        self.in_state['is_updated'] = True
                elif node == self.name:
                    self.in_state['is_updated'] = False
                    continue # we don't update our current node's distance
                else:
                    weight = int(weight)
                    if weight != self.in_state['nodes'].get(node, float("Inf")):
                        self.in_state["nodes"][node] = weight + self.in_state["nodes"][received_from]
                        self.in_state['is_updated'] = True
                        print "switch updated on ", self.in_state["nodes"][node]
   
        print self.name, self.in_state
        # Empty queue
        self.messages = []

        # TODO 2. Send neighbors updated distances               
        if self.in_state['is_updated']:
            for node in self.incoming_links:
               message = (self.name, ','.join(["{}{}".format(n, self.in_state["nodes"][n]) for n in self.in_state["nodes"]]))
               print node.name, message
               self.send_msg(message, node.name)

        # set to  off updated switch
        self.in_state['is_updated'] = False
        raw_input()


    def log_distances(self):
        ''' This function is called immedately after process_BF each round.  It 
        prints distances to the console and the log file in the following format (no whitespace either end):
        
        A:A0,B1,C2
        
        Where:
        A is the node currently doing the logging (self),
        B and C are neighbors, with vector weights 1 and 2 respectively
        NOTE: A0 shows that the distance to self is 0 '''
        
        # TODO: Use the provided helper function add_entry() to accomplish this task (see helpers.py).
        # An example call that which prints the format example text above (hardcoded) is provided. 
        add_entry(self.name, ','.join(["{}{}".format(n, self.in_state["nodes"][n]) for n in self.in_state["nodes"]]))
        #add_entry("A", "A0,B1,C2")        
