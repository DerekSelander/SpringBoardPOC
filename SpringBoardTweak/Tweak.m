//
//  DSTweak.m
//  SwizzlePOC
//
//  Created by Derek Selander on 5/2/16.
//  Copyright © 2016 Selander. All rights reserved.
//

#import <objc/runtime.h>

@import UIKit;
@implementation NSObject (DSTweak)

#pragma clang diagnostic push
#pragma clang diagnostic ignored "-Wundeclared-selector"


//#warning Uncomment load method to swizzle scrollViewDidScroll:

//+ (void)load
//{
//    static dispatch_once_t onceToken;
//    dispatch_once(&onceToken, ^{
//        Class swiftClass = NSClassFromString(@"SwizzlePOC.ViewController");
//        Class springBoardClass = NSClassFromString(@"SBFolderView");
//        
//        [NSObject swapClass:swiftClass originalInstanceMethod:@selector(scrollViewDidScroll:) swizzledSelector:@selector(tweak_scrollViewDidScroll:)];
//        [NSObject swapClass:springBoardClass originalInstanceMethod:@selector(scrollViewDidScroll:) swizzledSelector:@selector(tweak_scrollViewDidScroll:)];
//        NSLog(@"Content loaded.");
//    });
//}

#pragma clang diagnostic pop

+ (void)swapClass:(Class)class originalInstanceMethod:(SEL)originalSelector swizzledSelector:(SEL)swizzledSelector
{
    
    Method originalMethod = class_getInstanceMethod(class, originalSelector);
    Method swizzledMethod = class_getInstanceMethod([self class], swizzledSelector);
    
    
    BOOL didAddMethod =
    class_addMethod(class,
                    originalSelector,
                    method_getImplementation(swizzledMethod),
                    method_getTypeEncoding(swizzledMethod));
    
    if (didAddMethod) {
        class_replaceMethod(class,
                            swizzledSelector,
                            method_getImplementation(originalMethod),
                            method_getTypeEncoding(originalMethod));
    } else {
        method_exchangeImplementations(originalMethod, swizzledMethod);
    }
}


-(void)tweak_scrollViewDidScroll:(UIScrollView *)scrollView {
    [self tweak_scrollViewDidScroll:scrollView];
    // Call to original method, then we do our tweaks :]
    
    UIView *containerView = nil;
    if ([self isKindOfClass:NSClassFromString(@"SwizzlePOC.ViewController")]) {
        containerView = scrollView.subviews[0];
    } else {
        containerView = scrollView;
    }
    
    CGFloat contentOffset = scrollView.contentOffset.x;
    CGFloat width = CGRectGetWidth(scrollView.bounds);
    CGFloat rotation = (CGFloat)((NSInteger)contentOffset % (NSInteger)width) / width * 2.0 * M_PI;
    
    CATransform3D transform = CATransform3DMakeRotation(rotation, 0., 0., 1.);
    for (UIView *view in containerView.subviews) {
        view.layer.transform = transform;
    }
}

@end
