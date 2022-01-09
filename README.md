# AnyDisplay

## Overview

AnyDisplay provides wrapper code for rendering on different types of display,
primarily targeted at Raspberry Pi HATs.

This mainly consists of thin shims over the various different hardware
displays. The idea is to provide a single interface for them all,
[xkcd 927](https://xkcd.com/927/) notwithstanding.

## Details

As noted, the wrapper is mainly targeted at the different types of displays
available for the Raspberry Pi family of computers. The vast majority of these
specialist displays are in the form of HATs, which plug into the header.

By their nature, some of these displays are low resolution. We're not talking
320x200 here, we're talking 32x32, or lower. This might explain some of the
quirks of the interface which you find yourself wondering about.

## Requirements

The different displays will lazily import their requirements and these are not
marked as requirements for the library overall. This means that you will need to
install them "by hand". Typically, however, this is just a question of typing
`pip3 install blah` and you're done.

## Bugs and TODOs

The `Canvas` code is not _overly_ fast. It will run in reasonable speed on a Pi
4 but it's noticeably slow on a Pi Zero. It seems respectable on a Pi Zero 2
though. YMMV and all that.

It might be nice if the `Canvas` code were a little smarter about stretching
and/or cropping. It's already pretty complicated though and adding this is going
to require a bit of thought.