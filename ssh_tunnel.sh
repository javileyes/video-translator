#!/bin/bash
ssh -i .ssh/tunel -N root@74.208.163.90 -D "$1"
