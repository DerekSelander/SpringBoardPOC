#/usr/bin/env python

import lldb
import re
from random import randint

# Put _this_ file into ~/lldb/thread_return.py
# Put the following line into ~/.lldbinit
#     command script import ~/lldb/thread_return.py

def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand('command script add -f dump_methods.dump_methods dump_methods')

def dump_methods(debugger, command, result, internal_dict):
    '''dump_methods 

    dump_methods ViewControllerClass
    '''
    print '********************* Instance Methods ***********************'

    res = lldb.SBCommandReturnObject()

    # A fugly hack workaround for debugger.HandleCommand('po unsigned int $x') gets screwed up in the global namespace when redeclaring/re-executing script
    # Using 'unique' names to get around issue 
    instance_method_counter =  '$dump_methods_instance_method_counter'+ str(randint(0,1000000000000))
    class_method_counter =  '$dump_methods_class_method_counter'+ str(randint(0,10000000000000))

    class_methods = '$dump_methods_class_methods'+ str(randint(0,10000000000000))
    instance_methods = '$dump_methods_instance_methods'+ str(randint(0,10000000000000))

    instance_array = '$dump_method_instance_array'+str(randint(0,10000000000000))
    class_array = '$dump_method_class_array'+str(randint(0,10000000000000))

    debugger.HandleCommand('ex -l objc++ -- @import UIKit')
    debugger.HandleCommand('ex -l objc++ -- unsigned int '+ instance_method_counter +' = 0')
    debugger.HandleCommand('ex -l objc++ -- intptr_t * '+instance_methods+' = (intptr_t *)class_copyMethodList((id)objc_getClass("' + str(command) + '"), &' + instance_method_counter + ');')
    debugger.HandleCommand('ex -l objc++ -- NSMutableArray *'+instance_array+' = [NSMutableArray new];')
    debugger.HandleCommand('ex -l objc++ -- for (int i = 0; i < '+instance_method_counter+'; i++) {['+instance_array+' addObject: (id)[[NSString alloc] initWithFormat:@"%p -[%@ %@]", (intptr_t)method_getImplementation(('+instance_methods+')[i]), (id)NSClassFromString(@"' + str(command) + '"),((id)NSStringFromSelector((SEL)method_getName('+instance_methods+'[i])))]];}')
    debugger.HandleCommand('ex -l objc++ -o -- '+instance_array)
    debugger.GetCommandInterpreter().HandleCommand('ex -l objc++ -- ['+instance_array+' removeAllObjects]', res)

    print '********************* Class Methods ***********************'

    debugger.HandleCommand('ex -l objc++ -- NSMutableArray * '+class_array+' = [NSMutableArray new];')
    debugger.HandleCommand('ex -l objc++ -- unsigned int '+class_method_counter+' = 0;')
    debugger.HandleCommand('ex -l objc++ -- intptr_t * '+class_methods+' = (intptr_t *)class_copyMethodList((id)objc_getMetaClass("' + str(command) + '"), &'+class_method_counter+');')
    debugger.HandleCommand('ex -l objc++ -- for (int i = 0; i < '+class_method_counter+'; i++) {['+class_array+' addObject: (id)[[NSString alloc] initWithFormat:@"%p +[%@ %@]", (intptr_t)method_getImplementation(('+class_methods+')[i]), (id)NSClassFromString(@"' + str(command) + '"), ((id)NSStringFromSelector((SEL)method_getName('+class_methods+'[i])))]];}')
    debugger.HandleCommand('ex -l objc++ -o -- '+class_array)
    debugger.GetCommandInterpreter().HandleCommand('ex -l objc++ -- ['+class_array+' removeAllObjects]', res)

