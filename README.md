#### Important! Added a dump_methods.py script. Will spend a bit of time talking about custom LLDB scripts for finding stuff.

1. Grab latest. 
2. Put `dump_methods.py` in a known location. i.e. `~/lldb/`
3. Add the following to your `~/.lldbinit` file 
  ```lldb
  command script import PATH/TO/dump_methods.py
  
  # i.e. command script import ~/lldb/dump_methods.py
  ```
4. Celebrate! 


## Lab Material for [Silicon Valley iOS Developers' Meetup](http://www.meetup.com/sviphone/)

Part of my talk will include a lab where you will find and swizzle code from a stripped binary. Feel free to download this content and follow along during the talk. :] 

If you don't already have [class-dump, please download it](https://github.com/nygard/class-dump) and install in `/usr/local/bin` or similar location. 

##### For part of the lab, you will hunt for a class that implements some UIScrollViewDelegate methods. If you miss any steps or get behind, here they are.

Steps to find `UIScrollView`'s delegate class which implements `scrollViewDidScroll:` containing app icons in SpringBoard... without modding your `~/.lldbinit` file

1. Attach LLDB to SpringBoard

  ```lldb 
  lldb -n SpringBoard
  ```

2. Import heap search LLDB script  

  ```lldb
  (lldb) command script import lldb.macosx.heap
  ```

3. Search for all instances of UIScrollView in the heap, print out object description

  ```lldb 
  (lldb) objc_refs UIScrollView -o
  ```

4. Look for SBIconScrollView and the corresponding reference address (cmd + f could help). Note that your address will be different  

  ```lldb 
  (lldb) po 0xdeadbeef
  ```

5. Ensure that this is the correct UIScrollView. Augment the view in some way. 

  ```lldb 
  (lldb) po [0xdeadbeef setHidden: YES]
  (lldb) continue 
  ```

6. Looks like this is the correct reference you want to modify. Pause the program & undo your visual changes 

  ```lldb 
  (lldb) proc int
  (lldb) po [0xdeadbeef setHidden: NO]
  ```

7. UIScrollViews can have a UIScrollViewDelegate. Find out what class this is

  ```lldb 
  (lldb) po [0xdeadbeef delegate] 
  ```

8. It is this class (or subsequent parent class) that could implement UIScrollViewDelegate methods. Time to use `class-dump` on the executable itself. First you need to find where SpringBoard is located on your system. 

  ```lldb 
  ps aux | grep SpringBoard 
  ```

9. With the output apply class-dump to the SpringBoard executable 

  ```lldb 
  class-dump PATH/TO/SpringBoard 
  ```

Using the class that you printed out from the UIScrollView delgate, search for a class (or superclass) that implements `scrollViewDidScroll:`

