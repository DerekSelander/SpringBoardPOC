# Lab Material for [Silicon Valley iOS Developers Meetup](http://www.meetup.com/sviphone/),<br/> [iOS Security and Hacking](http://www.meetup.com/sviphone/events/230950259/)

## Slides

* Tip #1: Explore Code without the Source Code
  * Use registers
  * In 64-bit, objc_msgSend<br/>
    **RDI** is the instance of the class or class itself<br/>
    **RSI** is the selector<br/>
    **RDX** is the first param (if method has param/s)<br/>
    **RCX**, **R8**, **R9**, then stack if more params needed<br/>

  * In 32-bit a different calling convention is used. Use stack pointer offsets. 32-bit devices are iPhone 4s, iPad 2, iPhone 5c, etc.
    ```lldb
    (lldb) po *(id *)($esp + 4)     # $rdi equivalent 
    (lldb) po *(SEL *)($esp + 8)    # $rsi equivalent
    (lldb) # ecetera ... 
    ```
   For example, try attaching LLDB to the SpringBoard app, setting a breakpoint on every method in the SpringBoard executable, and then print the method. 
   ```lldb
   lldb -n SpringBoard
   (lldb) rb . -s SpringBoard        # Make sure to use the -s SpringBoard or else, it will create a breakpoint on EVERYTHING...
   Breakpoint 1: 31123 locations.
   (lldb) c
    Process 47674 resuming
    Process 47674 stopped
    * thread #1: tid = 0xe757cd, 0x0000000108daef79 SpringBoard`___lldb_unnamed_function25892$$SpringBoard, queue = 'com.apple.main-thread', stop reason = breakpoint 1.25892
    frame #0: 0x0000000108daef79 SpringBoard`___lldb_unnamed_function25892$$SpringBoard
    SpringBoard`___lldb_unnamed_function25892$$SpringBoard:
    ->  0x108daef79 <+0>: pushq  %rbp
    0x108daef7a <+1>: movq   %rsp, %rbp
    0x108daef7d <+4>: pushq  %r15
    0x108daef7f <+6>: pushq  %r14
    
   (lldb) po $rdi 
   <SBStatusBarStateAggregator: 0x7f9dda033e00>

   (lldb) po (SEL)$rsi
   "_restartTimeItemTimer"
   ```
  
  As you can see, `___lldb_unnamed_function25892$$SpringBoard` is LLDBs representation of `-[SBStatusBarStateAggregator_restartTimeItemTimer]` because the binary is stripped (no DEBUG info included)
  
* Tip #2: Find Instances of Classes
  * Use LLDB's heap script that comes included with every version of Xcode. In LLDB... 
  ```lldb
  (lldb) command script import lldb.macosx.heap
  (lldb) objc_refs -o UIViewController
  ``` 
  
  This will dump all instances of `UIViewController`s found in the heap. Also check out and play with `ptr_refs` & `malloc_info` from the same heap script. 
* Tip #3: Breakpoint Conditions
  * Break only when a particular case is true. Useful for hunting down a unique case for a frequently called method. 
    For example, say if you wanted to break when a specific UILabel's text is being set. In SpringBoard, when pressing the Do Not Distrub button, text appears saying "Do Not Distrub: On"

     ![Test Text](https://github.com/DerekSelander/SpringBoardPOC/raw/master/Media/Do_not_disturb.png)
   
   In LLDB, you can break exactly when this is set. 
   ```lldb 
   lldb -n SpringBoard
   (lldb) rb UILabel.setText: -c '(BOOL)[$rdx containsString:@"Do Not Disturb: On"]' # Remember, 64-bit for this to work
   ``` 
   
   Now, tap on the Do Not Distrub Button. Breakpoint hit :] 
   
* Tip #4: Complex Assembly
 * Sometimes the assembly is to hard to read by itself. As a workaround, you can execute the code while stepping in the assembly to figure out what is happening 
 * Create a breakpoint then call the function in which you want to examine. Dump registers while stepping through asm.
   For example, in iOS 9.3 Simulator 6s Plus, SpringBoard has the following method: `[[SBPasscodeController sharedInstance] forceUserToChangePasscode]` found at `___lldb_unnamed_function7503$$SpringBoard`  

 ```lldb
 lldb -n SpringBoard
 (lldb) b ___lldb_unnamed_function7503$$SpringBoard
 (lldb) ex -i false -o -- [[SBPasscodeController sharedInstance] forceUserToChangePasscode]
 (lldb) di 
 (lldb) si 
 ```

 You can step through instructions and print values in assembly. 
  
* Tip #5: Use LLDB Python API
 * Use the LLDB Python API 
 ```lldb
 (lldb) script 
 >>> target = lldb.debugger.GetSelectedTarget()
 >>> path = target.executable.fullpath
 >>> print path 
 ```
 You can of course make scripts to do these tasks so you don't have to enter in these commands every time. 
 Here is an example of `dump_methods.py` used on a class in SpringBoard. 
 
 ![Test Text](https://github.com/DerekSelander/SpringBoardPOC/raw/master/Media/dump_methods.png)
 
 `dump_methods.py` is included in this repo. 
 
 
 
 Here's a different (private) command called `stripped regex lookup` that I have been working on that does a regex on the input and finds the physical address as well as the `___lldb_unnamed_function` equivalent for the query on a stripped binary. :]
 
 ![Test Text](https://github.com/DerekSelander/SpringBoardPOC/raw/master/Media/srl.png)
 
## Setup 

If you don't already have [class-dump, please download it](https://github.com/nygard/class-dump) and install in `/usr/local/bin` or similar location. 

Download this sample project and follow along below. 

There's a LLDB script included called `dump_methods.py` used for well... dumping methods. You can install it by following these instructions: 

1. Put `dump_methods.py` in a known location. i.e. `~/lldb/`
2. Add the following to your `~/.lldbinit` file 
  ```lldb
  command script import PATH/TO/dump_methods.py
  
  # i.e. command script import ~/lldb/dump_methods.py
  ```
3. Celebrate!

From here on out, every time LLDB is launched you can use this script for getting all the methods. i.e. `(lldb) dump_methods UIView`

## Compiling the Code

After downloading the sample code, build and run the app. It is an application which has a UIScrollView which showcases several views... not too exciting. Try scrolling back and forth in the simulator to make sure this works.

The majority of work is done in Interface Builder. Take a look at `ViewController.swift`: The UIScrollView's delegate is assigned to `ViewController.swift`, which implements only one method from UIScrollViewDelegate, `scrollViewDidScroll:` 

An important note is that SpringBoardPOC has one required framework, `SpringBoardTweak`. The one class in this framework is called `Tweak.m`. Open up `Tweak.m` and explore it's contents. 

You'll see a commented out method for `+ (void)load`. Uncomment this method then recompile the app. Try moving the UIScrollView around and see what happens. 

## Finding Where to Swizzle

In this lab you will find the location of the delegate method of SBIconScrollView, a subclass of UIScrollView which is used to display the SpringBoard icons. 

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

4. Ensure that this is the correct UIScrollView subclass. Augment the view in some way. 

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

6. UIScrollViews can have a `delegate` object conforming to `UIScrollViewDelegate`. Find out if this class exists and if it does, what class this is...

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
  class-dump PATH/TO/SpringBoard -f scrollViewDidScroll
  ```

  ![Test Text](https://github.com/DerekSelander/SpringBoardPOC/raw/master/Media/Terminal.gif)
  Using the class that you printed out from the UIScrollView delgate, search for a class (or superclass) that implements `scrollViewDidScroll:`

  As you can see, `SBFolderView` (and by inheritance, all of it's subclasses) implement `scrollViewDidScroll:`

9. Head back to the LLDB console. Type the following, but *DO NOT PRESS ENTER YET*
  ```lldb
  (lldb) process load 
  ```

  Provided that you've already compiled the SpringBoardPOC app. Open the products directory, right click on `SpringBoardTweak.framework` and select `Show in Finder`. Expand the SpringBoardTweak.framework and drag and drop the `SpringBoardTweak` executable into the LLDB console. Now press enter. Resume the program
 
  ![Test Text](https://github.com/DerekSelander/SpringBoardPOC/raw/master/Media/LLDB_Load_DYLD.gif)


## Where to Go From Here

If this stuff interests you there are several paths you can take. 

If you want to learn more, I would suggest following along on this tutorial. Although it's a bit dated, you'll learn some good debugging tricks in this series. 

https://www.raywenderlich.com/94020/creating-an-xcode-plugin-part-1  
https://www.raywenderlich.com/97756/creating-an-xcode-plugin-part-2  
https://www.raywenderlich.com/104479/creating-an-xcode-plugin-part-3  

An EXCELLENT book on the process of creating jailbreak tweaks check out:  

https://github.com/iosre/iOSAppReverseEngineering

One path is to try figuring out how some features in an application work. If that interests you, here are some challenges: 

* Replace the camera image template from the slideup menu with a different image and different action. For example: open Safari instead. 
  ![Test Text](https://github.com/DerekSelander/SpringBoardPOC/raw/master/Media/SpringBoardSlide.png) 
  I'll give you a starting point to work off of: 

  ```lldb
  lldb -n SpringBoard
  (lldb) rb UIControl.send 
  (lldb) c 
  ```
  Tap on button. LLDB will stop on `-[UIControl sendAction:to:forEvent:]`. Explore registers. Remember to work ona 64 bit device. (IMHO, it's easier :] ) 
  ```lldb 
  (lldb) po (SEL)$rdx 
  (lldb) po rcx 
  ```
  
  This will dump the SEL and the recipient. See if you can go from there... 


* The Photos application in the Simulator has a very cool effect when scrolling through the photos (only found in iOS 9 and later). When you scroll, part of the photo gets cut off, giving it a cool 3-Dimensional affect. Try and figure out how they accomplish this. 

  ```lldb
  lldb -n MobileSlideShow
  ```
  
* What API endpoints is the Maps application hitting? What params are they using? Try and get as much information out of it as possible. Are you able to hit these endpoints yourself with Terminal's `curl`? 

  ```lldb
  lldb -n Maps
  ```

#### *Note: I have not tried any of these challenges, so I do not know the difficulty of completing them. I'll be open to solving them myself and giving hints if I see an honest attempt is being made* 


![Test Text](https://github.com/DerekSelander/SpringBoardPOC/raw/master/Media/LLDB_Load_DYLD.gif)


