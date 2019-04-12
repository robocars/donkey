#!/bin/sh
name="data-$(date '+%Y-%m-%d_%H-%M-%S').tar.gz"
echo $name
tar -cvzf "$name" /d2-tmpfs/*
echo $name

