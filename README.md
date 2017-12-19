# Go away condor!

Hey you! Do you like overengineered solutions to completely unnecessary problems? Me too!

My name is Cassandra and I wrote a python code to keep condor users off of your Peyton desktop!


  - How does it work?
This code monitors the memory and cpu percentage usage of other users on your computer and if they use more than a set threshold, it spawns some pointless processes to remind Condor that you are using this computer and don't need someone using your RAM!

  - What is this project?
Peyton Hall desktop computers have a computing cluster called Condor installed on them, for utilizing not-in-use desktops. However, this cluster is notorious for using your resources when you need them! 

In theory Condor vacates your computer when you start using resources, but in practice this does not happen immediately, and it will use your memory and processing resources if you don't have all four cores busy. For some of us, this can be a huge problem! They can spike your RAM usage and crash already running code if Condor can't tell that you're working here! 

  - This is an overengineered mess of a module.
Yes. 
