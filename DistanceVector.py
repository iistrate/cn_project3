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

class DistanceVector(Node):
    
    def __init__(self, name, topolink, outgoing_links, incoming_links):
        ''' Constructor. This is run once when the DistanceVector object is
        created at the beginning of the simulation. Initializing data structure(s)
        specific to a DV node is done here.'''

        super(DistanceVector, self).__init__(name, topolink, outgoing_links, incoming_links)
        #TODO: Create any necessary data structure(s) to contain the Node's internal state / distance vector data    
        self.in_state = dict()
        self.in_state["nodes"]={"{}".format(self.name):0}
        self.in_state["is_updated"]=False

    def send_initial_messages(self):
        ''' This is run once at the beginning of the simulation, after all
        DistanceVector objects are created and their links to each other are
        established, but before any of the rest of the simulation begins. You
        can have nodes send out their initial DV advertisements here. 

        Remember that links points to a list of Neighbor data structure.  Access
        the elements with .name or .weight '''

        # TODO - Each node needs to build a message and send it to each of its neighbors
        # HINT: Take a look at the skeleton methods provided for you in Node.py
        for node in self.incoming_links:
            message = (self.name, "{node_name}{distance_cost}".format(node_name=self.name, distance_cost=0))
            self.send_msg(message, node.name)


    def process_BF(self):
        ''' This is run continuously (repeatedly) during the simulation. DV
        messages from other nodes are received here, processed, and any new DV
        messages that need to be sent to other nodes as a result are sent. '''
        # Implement the Bellman-Ford algorithm here.  It must accomplish two tasks below:
        # TODO 1. Process queued messages
        vector = set(["{}{}".format(node, self.in_state["nodes"][node]) for node in self.in_state["nodes"]])
        vector_copy = vector.copy()
        for msg in self.messages:                        
            received_from, vector = msg
            for vector_bit in vector.split(','):
                node, weight, _ = re.split(r'(-?[0-9]+)', vector_bit)
                
                if node == self.name:
                    continue
                if node not in self.in_state["nodes"].keys():
                    # if node is a direct neighbor
                    if node in [n.name for n in self.outgoing_links]:
                        self.in_state["nodes"][node] = int(self.get_outgoing_neighbor_weight(node))
                    else:
                        self.in_state["nodes"][node] = int(weight) + self.in_state["nodes"][received_from]

                # if we already know of the node
                else:
                    n_w = self.get_outgoing_neighbor_weight(received_from)
                    try:
                        n_w = int(n_w) + int(weight)
                        if int(weight) <= -99:
                            self.in_state["nodes"][node] = -99                         
                        elif n_w <  self.in_state["nodes"][node]:
                            self.in_state["nodes"][node] = n_w
                    except BaseException, e:
                        pass
   
        # Empty queue
        self.messages = []
        
        vector = set(["{}{}".format(node, self.in_state["nodes"][node]) for node in self.in_state["nodes"]])
        # TODO 2. Send neighbors updated distances              
        if vector - vector_copy:
            for node in self.incoming_links:
               message = (self.name, ','.join(["{}{}".format(n, self.in_state["nodes"][n]) for n in self.in_state["nodes"]]))
               self.send_msg(message, node.name)
            
            self.in_state['is_updated'] = False
#        raw_input()

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
