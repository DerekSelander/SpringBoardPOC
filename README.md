#### Important! Added a dump_methods.py script. Will spend a bit of time talking about custom LLDB scripts for finding stuff.

1. Grab latest. 
2. Put `dump_methods.py` in a known location. i.e. `~/lldb/`
3. Add the following to your `~/.lldbinit` file 
  ```lldb
  command script import PATH/TO/dump_methods.py
  
  # i.e. command script import ~/lldb/dump_methods.py
  ```
4. Celebrate! 

![Test Text](https://github.com/DerekSelander/SpringBoardPOC/raw/master/Media/LLDB_Load_DYLD.gif)


## Lab Material for [Silicon Valley iOS Developers Meetup](http://www.meetup.com/sviphone/), [iOS Security and Hacking](http://www.meetup.com/sviphone/events/230950259/)

If you don't already have [class-dump, please download it](https://github.com/nygard/class-dump) and install in `/usr/local/bin` or similar location. 

##### Finding Where to Swizzle

In this lab you will find the location of the delegate method of SBIconScrollView, a subclass of UIScrollView which is used to display on the SpringBoard icons. 

Steps to find `UIScrollView`'s delegate class which implements `scrollViewDidScroll:` containing app icons in SpringBoard... without modding your `~/.lldbinit` file

1. Attach LLDB to SpringBoard. Alternatively, use Xcode. From the top menu, select `Debug`, then `Attach to process`, then type in `SpringBoard`. 

  ![Test Text](https://github.com/DerekSelander/SpringBoardPOC/raw/master/Media/LLDB_Attach.gif)

  Or if you want to use Terminal... 

  ```lldb 
  lldb -n SpringBoard
  ```

2. Import heap search LLDB script, then look for all the instances of SBIconScrollView

  ```lldb
  (lldb) command script import lldb.macosx.heap
  (lldb) objc_refs SBIconScrollView -o
  ```

![Test Text](https://github.com/DerekSelander/SpringBoardPOC/raw/master/Media/LLDB_Find.gif)

3. Look for SBIconScrollView and the corresponding reference address (cmd + f could help). Note that your address will be different  

  ```lldb 
  (lldb) po 0xdeadbeef
  ```

4. Ensure that this is the correct UIScrollView. Augment the view in some way. 

  ```lldb 
  (lldb) po [0xdeadbeef setHidden: YES]
  (lldb) continue 
  ```

  ... Looks like this is the correct reference you want to modify. Pause the program & undo your visual changes 

  ```lldb 
  (lldb) proc int
  (lldb) po [0xdeadbeef setHidden: NO]
  ```

  ![Test Text](https://github.com/DerekSelander/SpringBoardPOC/raw/master/Media/LLDB_SBIconScrollView.gif)

6. UIScrollViews can have a UIScrollViewDelegate. Find out what class this is

  ```lldb 
  (lldb) po [0xdeadbeef delegate] 
  (lldb) po [[0xdeadbeef delegate] superclass]
  ```

![Test Text](https://github.com/DerekSelander/SpringBoardPOC/raw/master/Media/LLDB_SBIconScrollView_Delegate.gif)

7. It is this class (or subsequent parent class) that could implement UIScrollViewDelegate methods. Time to use `class-dump` on the executable itself. First you need to find where SpringBoard is located on your system. 

  ```lldb 
  ps aux | grep SpringBoard 
  ```

8. With the output apply class-dump to the SpringBoard executable 

  ```lldb 
  class-dump PATH/TO/SpringBoard 
  ```

Using the class that you printed out from the UIScrollView delgate, search for a class (or superclass) that implements `scrollViewDidScroll:`

