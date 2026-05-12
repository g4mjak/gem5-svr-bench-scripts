#!/usr/bin/env bash

green="\033[1;92m"
yellow="\033[1;93m"
orange="\033[38;5;214m"
bold="\033[1m"
red="\033[1;31m"
dark_orange="\033[38;5;208m"
reset="\033[0m"

bar_length=60
lines=12   # updated line count

clear_line() {
  printf "\033[2K\r"
}

make_bar() {
  count=$1
  total=$2
  length=$3

  if [ "$total" -eq 0 ]; then
    printf "%-${length}s" ""
    return
  fi

  # calculate filled proportion
  filled=$(( (count * length + total - 1) / total ))  # round up

  # print bar
  for i in $(seq 1 $length); do
    if [ "$i" -le "$filled" ]; then
      printf "|"
    else
      printf " "
    fi
  done
}

draw() {
  status=$(pueue status)

  finished=$(echo "$status" | grep -cE "\bSuccess\b")
  running=$(echo "$status" | grep -cE "\bRunning\b")
  queued=$(echo "$status" | grep -cE "\bQueued\b")
  paused=$(echo "$status" | grep -cE "\bPaused\b")
  failed=$(echo "$status" | grep -cE "\bFailed\b")
  killed=$(echo "$status" | grep -cE "\bKilled\b")

  total=$((finished + running + queued + paused + failed + killed))

  clear_line; printf "\n                            ${bold}Pueue Status Dashboard${reset}\n"
  clear_line; printf "${bold}------------------------------------------------------------------------------${reset}\n"

  clear_line; printf " Finished: [${green}%s${reset}] %d\n" "$(make_bar $finished $total $bar_length)" "$finished"
  clear_line; printf " Running:  [${bold}%s${reset}] %d\n" "$(make_bar $running  $total $bar_length)" "$running"
  clear_line; printf " Queued:   [${yellow}%s${reset}] %d\n" "$(make_bar $queued   $total $bar_length)" "$queued"
  clear_line; printf " Paused:   [${orange}%s${reset}] %d\n" "$(make_bar $paused   $total $bar_length)" "$paused"
  clear_line; printf " Killed:   [${dark_orange}%s${reset}] %d\n" "$(make_bar $killed  $total $bar_length)" "$killed"
  clear_line; printf " Failed:   [${red}%s${reset}] %d\n" "$(make_bar $failed   $total $bar_length)" "$failed"

  clear_line; printf "${bold}------------------------------------------------------------------------------${reset}\n"
  clear_line; printf "                                  ${bold}Total:${reset} %d\n" "$total"
  clear_line; printf "${bold}------------------------------------------------------------------------------${reset}\n\n"
}

draw