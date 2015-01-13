#!/usr/bin/env bash


mongoimport --file ../texts/qualaroo_csv.txt --type csv --headerline --drop -d bj -c qualaroo
