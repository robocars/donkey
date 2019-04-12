#!/bin/sh
for IRQ in /proc/irq/*/smp_affinity;
  do
    [ -f $IRQ ] || continue
    echo -n 0f > $IRQ
  done

