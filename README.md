# Go away condor!

Hey you! Do you like overengineered solutions to completely unnecessary problems? Me too!

My name is Cassandra and I wrote a python code to keep condor users off of your Peyton desktop!


  - How does it work?
  
This code monitors the memory and cpu percentage usage of other users on your computer and if they use more than a set threshold, it spawns some pointless processes to remind Condor that you are using this computer and don't need someone using your RAM!

It runs a few processes, maximizing your CPU usage for a couple minutes, then stops. By that point, Condor typically leaves, but if it doesn't work, it will rinse and repeat. 

  - What is this project?
  
Peyton Hall desktop computers have a computing cluster called Condor installed on them, for utilizing not-in-use desktops. However, this cluster is notorious for using your resources when you need them! This used to be a huge problem, but is mostly resolved since the system has been adjusted. 

  - How do I use this code?

Run it as a script. Or if you want to customize for your own usage, call main() with various parameters - they're pretty self explanatory.
