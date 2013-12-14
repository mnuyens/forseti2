#!/bin/sh

lcm-gen -p types/*.lcm
lcm-gen -j types/*.lcm
lcm-gen --csharp types/*.lcm

