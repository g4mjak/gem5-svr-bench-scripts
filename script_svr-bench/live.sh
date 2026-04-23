#!/usr/bin/env bash
lines=12
status
sleep 5
printf "\033[?25l"
trap 'printf "\033[?25h"; exit' INT TERM EXIT

while true; do
  printf "\033[${lines}A"
  status

  first_run=false
  sleep 5
done

