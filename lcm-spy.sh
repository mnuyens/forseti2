#!/bin/sh

lcm-gen -j types/*.lcm
javac -cp .:lcm.jar forseti2/*.java
jar cvf forseti2/forseti2.jar forseti2/*.class
export CLASSPATH=$CLASSPATH:./forseti2/forseti2.jar
alias java='java -ea -server'
lcm-spy --lcm-url='udpm://239.255.76.67:7667?ttl=1'
